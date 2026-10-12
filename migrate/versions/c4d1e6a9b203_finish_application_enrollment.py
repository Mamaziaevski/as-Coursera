from alembic import op
import sqlalchemy as sa

revision = "c4d1e6a9b203"
down_revision = "bff785e73430"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('application', schema=None) as batch_op:
        batch_op.add_column(sa.Column('student_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('course_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('manager_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_application_student', 'user', ['student_id'], ['id'])
        batch_op.create_foreign_key('fk_application_course', 'course', ['course_id'], ['id'])
        batch_op.create_foreign_key('fk_application_manager', 'user', ['manager_id'], ['id'])

    with op.batch_alter_table('enrollment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('student_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('group_id', sa.Integer(), nullable=False))
        batch_op.create_unique_constraint('uq_enrollment_student_group', ['student_id', 'group_id'])
        batch_op.create_foreign_key('fk_enrollment_student', 'user', ['student_id'], ['id'])
        batch_op.create_foreign_key('fk_enrollment_group', 'studygroup', ['group_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('refresh_token', sa.String(length=512), nullable=True))
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.create_unique_constraint('uq_user_email', ['email'])




def downgrade():

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_email', type_='unique')
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.drop_column('refresh_token')

    with op.batch_alter_table('enrollment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_enrollment_group', type_='foreignkey')
        batch_op.drop_constraint('fk_enrollment_student', type_='foreignkey')
        batch_op.drop_constraint('uq_enrollment_student_group', type_='unique')
        batch_op.drop_column('group_id')
        batch_op.drop_column('student_id')

    with op.batch_alter_table('application', schema=None) as batch_op:
        batch_op.drop_constraint('fk_application_manager', type_='foreignkey')
        batch_op.drop_constraint('fk_application_course', type_='foreignkey')
        batch_op.drop_constraint('fk_application_student', type_='foreignkey')
        batch_op.drop_column('manager_id')
        batch_op.drop_column('course_id')
        batch_op.drop_column('student_id')


