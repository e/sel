from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from student.models import AnonymousUserId
from submissions.models import Submission


# Quick hack to Dump open ended answers for a specific course to a text file
# delimited by tabs. Copy to
# /edx/app/edxapp/edx-platform/common/djangoapps/student/management/commands/

class Command(BaseCommand):

    help = """
    Dumps open ended answers for a specific course to a text file delimited by
    tabs.
    Example:
          $ ... oeacsv -c some/course/id -o /mpt/oea.csv
    """

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course_id',
                    default=False,
                    help="course id to use for transfer"),
        make_option('-o', '--output_file',
                    metavar='OUTPUT_FILE',
                    dest='output_file',
                    default='/tmp/oea.csv',
                    help="output file"),
    )

    def handle(self, *args, **options):
        if not options['course_id']:
            raise CommandError("You must specify a course id for this command")
        if not options['output_file']:
            raise CommandError('You must specify an output file')
        s = Submission.objects.filter(
            student_item__course_id=options['course_id'])
        data={}
        q = []
        for item in s:
            user=AnonymousUserId.objects.get(
                anonymous_user_id=item.student_item.student_id).user
            name = user.profile.name
            data[name] = {}
            if item.student_item.item_id not in q:
                q.append(item.student_item.item_id)

        for item in s:
            user=AnonymousUserId.objects.get(
                anonymous_user_id=item.student_item.student_id).user
            name = user.profile.name
            data[name][item.student_item.item_id] = item.raw_answer.decode(
                'utf8')

        with open(options['output_file'], 'wb') as f:
            f.write('\t')
            for question in q:
                f.write(question.encode('utf8') + '\t')
            f.write('\n')
            for item in data:
                f.write(item.encode('utf8') + '\t')
                for question in q:
                    try:
                        f.write(data[item][question].encode('utf8') + '\t')
                    except:
                        f.write('\t')
                f.write('\n')

