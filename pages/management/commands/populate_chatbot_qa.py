"""
Management command to populate the PublicAnswer model with Q&A from site content.
Usage: python manage.py populate_chatbot_qa
"""
from django.core.management.base import BaseCommand
from pages.models_chatbot import PublicAnswer


class Command(BaseCommand):
    help = 'Populate the chatbot knowledge base with Q&A from site content'

    def handle(self, *args, **options):
        self.stdout.write('Starting chatbot Q&A population...')
        
        # Clear existing answers if desired (uncomment to enable)
        # PublicAnswer.objects.all().delete()
        
        # Define Q&A entries
        qa_entries = [
            # About Chapter
            {
                'question': 'What is Nu Gamma Sigma Chapter?',
                'keywords': 'nu gamma sigma chapter about fraternity phi beta sigma belleville',
                'answer': 'Nu Gamma Sigma Chapter is an alumni chapter of Phi Beta Sigma Fraternity, Inc. serving Belleville, Illinois and the surrounding communities of St. Clair County and Madison County. Chartered on May 21, 2002, we are dedicated to the fraternity\'s mission of "Culture for Service and Service for Humanity."',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'Where is Nu Gamma Sigma Chapter located?',
                'keywords': 'location belleville illinois st clair madison county',
                'answer': 'Nu Gamma Sigma Chapter is located in Belleville, Illinois, serving the St. Clair County and Madison County areas. Our mailing address is P.O. Box 23183, Belleville, IL 62223-9294.',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'When was Nu Gamma Sigma Chapter chartered?',
                'keywords': 'chartered founding date may 2002',
                'answer': 'Nu Gamma Sigma Chapter was chartered on May 21, 2002. We are part of the Great Lakes Region of Phi Beta Sigma Fraternity, Inc.',
                'category': 'history',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'Who is the current president of Nu Gamma Sigma?',
                'keywords': 'president ronald mcclellan leadership',
                'answer': 'Ronald McClellan serves as the Chapter President of Nu Gamma Sigma Chapter.',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'What is Phi Beta Sigma\'s motto?',
                'keywords': 'mission motto culture service humanity',
                'answer': 'The guiding principle of Phi Beta Sigma Fraternity, Inc. is "Culture for Service and Service for Humanity."',
                'category': 'values',
                'is_active': True,
                'confidence_threshold': 30
            },
            # Membership
            {
                'question': 'How can I join Phi Beta Sigma?',
                'keywords': 'join membership apply requirements eligibility',
                'answer': 'Nu Gamma Sigma Chapter is an Alumni Chapter, so we accept membership applications from professional men who have earned a baccalaureate or higher degree from a recognized college or university. Candidates cannot hold active or previous membership in another intercollegiate fraternity. To learn more, please contact us.',
                'category': 'membership',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'What are the collegiate membership requirements?',
                'keywords': 'collegiate membership requirements gpa college university',
                'answer': 'For collegiate membership, candidates must: (1) be actively working toward a baccalaureate degree at a recognized college or university, (2) have completed at least one grading period, and (3) have a minimum 2.5 cumulative GPA on a four-point scale.',
                'category': 'membership',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'What are the alumni membership requirements?',
                'keywords': 'alumni membership requirements degree professional',
                'answer': 'For alumni membership, candidates must have earned a baccalaureate degree or other degree from a recognized college or university. Nu Gamma Sigma Chapter accepts alumni membership applications from professional men in the Belleville and surrounding areas.',
                'category': 'membership',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'Can I transfer from another fraternity?',
                'keywords': 'transfer fraternity other membership another',
                'answer': 'No, candidates for Phi Beta Sigma cannot hold active or previous membership in another intercollegiate fraternity, other than an honorary or professional fraternity. This is a core requirement of the organization.',
                'category': 'membership',
                'is_active': True,
                'confidence_threshold': 30
            },
            # Programs
            {
                'question': 'What programs does Nu Gamma Sigma offer?',
                'keywords': 'programs business education social action mentorship',
                'answer': 'Nu Gamma Sigma Chapter offers several programs including Business Initiatives, Social Action Programs, Educational Development, and Youth Mentorship. Each program is designed to serve the community and support our mission of service to humanity.',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'What is the Sigma Beta Club?',
                'keywords': 'sigma beta club youth mentorship program',
                'answer': 'The Sigma Beta Club is a youth mentorship and development program operated by Phi Beta Sigma Chapter. It provides young men with opportunities for educational advancement, leadership development, and community service.',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            # Events
            {
                'question': 'When does Nu Gamma Sigma hold events?',
                'keywords': 'events calendar schedule when',
                'answer': 'Nu Gamma Sigma Chapter hosts various events throughout the year. Please visit our Events page or contact us for the current calendar of activities and events.',
                'category': 'events',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'How can I attend Nu Gamma Sigma events?',
                'keywords': 'attend events community public invited',
                'answer': 'Community members and friends are often welcome at our chapter events. Please check our Events page for upcoming activities or contact us directly to inquire about specific events you\'d like to attend.',
                'category': 'events',
                'is_active': True,
                'confidence_threshold': 30
            },
            # Contact & General
            {
                'question': 'How can I contact Nu Gamma Sigma Chapter?',
                'keywords': 'contact us email phone address reach',
                'answer': 'You can contact Nu Gamma Sigma Chapter by visiting our Contact Us page or mailing us at P.O. Box 23183, Belleville, IL 62223-9294. We look forward to hearing from you!',
                'category': 'contact',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'What is the mission of Nu Gamma Sigma?',
                'keywords': 'mission purpose community service leadership',
                'answer': 'Our mission is to bring together professional men dedicated to advancing Phi Beta Sigma\'s guiding principle of "Culture for Service and Service for Humanity." We focus on educational initiatives, youth development, community outreach, and economic empowerment programs.',
                'category': 'values',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'Is Nu Gamma Sigma affiliated with a college?',
                'keywords': 'college university affiliated campusate',
                'answer': 'Nu Gamma Sigma is an alumni chapter and is not affiliated with a specific college or university. Our members are professional men from the Belleville and surrounding communities who have graduated from various institutions.',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'What region is Nu Gamma Sigma in?',
                'keywords': 'region great lakes regional area',
                'answer': 'Nu Gamma Sigma Chapter is part of the Great Lakes Region of Phi Beta Sigma Fraternity, Inc. This region includes chapters across several states focused on collaborative programming and regional unity.',
                'category': 'about',
                'is_active': True,
                'confidence_threshold': 30
            },
            # Frequently Asked
            {
                'question': 'What does "Culture for Service" mean?',
                'keywords': 'culture service humanity meaning principle',
                'answer': '"Culture for Service and Service for Humanity" is the guiding principle of Phi Beta Sigma. It emphasizes the importance of using culture, learning, and resources to serve others and uplift humanity.',
                'category': 'values',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'How often does Nu Gamma Sigma meet?',
                'keywords': 'meeting frequency chapters meetings gathering',
                'answer': 'Nu Gamma Sigma Chapter holds regular meetings and events. For specific meeting schedules and frequencies, please contact us directly or visit our Events page.',
                'category': 'faq',
                'is_active': True,
                'confidence_threshold': 30
            },
            {
                'question': 'Can non-members attend our events?',
                'keywords': 'non-members community guests public attendance',
                'answer': 'Many of our community events and programs are open to the general public. However, some chapter meetings and internal events are restricted to members. Please contact us to ask about specific events.',
                'category': 'faq',
                'is_active': True,
                'confidence_threshold': 30
            },
        ]
        
        # Create or update Q&A entries
        created_count = 0
        updated_count = 0
        
        for qa in qa_entries:
            _, created = PublicAnswer.objects.update_or_create(
                question=qa['question'],
                defaults={
                    'keywords': qa['keywords'],
                    'answer': qa['answer'],
                    'category': qa['category'],
                    'is_active': qa['is_active'],
                    'confidence_threshold': qa['confidence_threshold'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {qa["question"][:50]}...')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated: {qa["question"][:50]}...')
                )
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(f'✓ Created: {created_count} new Q&A entries')
        self.stdout.write(f'⟳ Updated: {updated_count} existing Q&A entries')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Chatbot Q&A population completed successfully!'))
