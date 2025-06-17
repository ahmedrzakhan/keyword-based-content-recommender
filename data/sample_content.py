import json
from datetime import datetime, timedelta
import random

def generate_sample_content():
    """Generate diverse sample content for the recommendation system."""
    
    content_data = [
        # Technology Content
        {
            "id": "1",
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn patterns and make predictions.",
            "category": "Technology",
            "tags": ["AI", "ML", "Data Science", "Algorithms"],
            "difficulty": "Beginner",
            "read_time": 5,
            "author": "Dr. Sarah Chen",
            "created_at": "2024-01-15"
        },
        {
            "id": "2",
            "title": "Deep Learning Neural Networks Explained",
            "content": "Deep learning uses artificial neural networks with multiple layers to model and understand complex patterns. These networks can automatically extract features from raw data, making them powerful for tasks like image recognition and natural language processing.",
            "category": "Technology",
            "tags": ["Deep Learning", "Neural Networks", "AI", "Pattern Recognition"],
            "difficulty": "Intermediate",
            "read_time": 8,
            "author": "Prof. Michael Rodriguez",
            "created_at": "2024-01-20"
        },
        {
            "id": "3",
            "title": "Cloud Computing Fundamentals",
            "content": "Cloud computing delivers computing services over the internet, including servers, storage, databases, networking, software, and analytics. It offers faster innovation, flexible resources, and economies of scale.",
            "category": "Technology",
            "tags": ["Cloud", "AWS", "Infrastructure", "Scalability"],
            "difficulty": "Beginner",
            "read_time": 6,
            "author": "Jennifer Kim",
            "created_at": "2024-01-25"
        },
        {
            "id": "4",
            "title": "Cybersecurity Best Practices",
            "content": "Cybersecurity involves protecting digital systems, networks, and data from malicious attacks. Key practices include using strong passwords, enabling two-factor authentication, keeping software updated, and being cautious with email attachments.",
            "category": "Technology",
            "tags": ["Security", "Privacy", "Network", "Protection"],
            "difficulty": "Intermediate",
            "read_time": 7,
            "author": "Alex Thompson",
            "created_at": "2024-02-01"
        },
        {
            "id": "5",
            "title": "Blockchain Technology Overview",
            "content": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography. It enables secure, transparent, and decentralized transactions.",
            "category": "Technology",
            "tags": ["Blockchain", "Cryptocurrency", "Decentralization", "Security"],
            "difficulty": "Advanced",
            "read_time": 10,
            "author": "David Park",
            "created_at": "2024-02-05"
        },
        
        # Science Content
        {
            "id": "6",
            "title": "Climate Change and Global Warming",
            "content": "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, scientific evidence shows that human activities have been the main driver of climate change since the 1800s.",
            "category": "Science",
            "tags": ["Climate", "Environment", "Global Warming", "Sustainability"],
            "difficulty": "Beginner",
            "read_time": 6,
            "author": "Dr. Emily Watson",
            "created_at": "2024-01-18"
        },
        {
            "id": "7",
            "title": "CRISPR Gene Editing Technology",
            "content": "CRISPR-Cas9 is a revolutionary gene-editing technology that allows scientists to make precise changes to DNA. It has potential applications in treating genetic diseases, improving crops, and advancing biological research.",
            "category": "Science",
            "tags": ["Genetics", "Biotechnology", "Medicine", "DNA"],
            "difficulty": "Advanced",
            "read_time": 12,
            "author": "Dr. Robert Lee",
            "created_at": "2024-01-22"
        },
        {
            "id": "8",
            "title": "Quantum Physics Basics",
            "content": "Quantum physics is the branch of physics that studies matter and energy at the smallest scales. It describes phenomena that are counterintuitive, such as particles existing in multiple states simultaneously until observed.",
            "category": "Science",
            "tags": ["Physics", "Quantum", "Particles", "Theory"],
            "difficulty": "Advanced",
            "read_time": 15,
            "author": "Prof. Lisa Chang",
            "created_at": "2024-02-08"
        },
        {
            "id": "9",
            "title": "Renewable Energy Sources",
            "content": "Renewable energy comes from natural sources that are constantly replenished, such as sunlight, wind, rain, tides, and geothermal heat. These sources are sustainable alternatives to fossil fuels and help reduce greenhouse gas emissions.",
            "category": "Science",
            "tags": ["Energy", "Solar", "Wind", "Sustainability", "Environment"],
            "difficulty": "Beginner",
            "read_time": 7,
            "author": "Dr. Mark Johnson",
            "created_at": "2024-02-12"
        },
        {
            "id": "10",
            "title": "Space Exploration and Mars Missions",
            "content": "Space exploration involves the investigation of outer space through robotic spacecraft and human spaceflight. Recent Mars missions have provided valuable data about the planet's geology, atmosphere, and potential for past or present life.",
            "category": "Science",
            "tags": ["Space", "Mars", "NASA", "Exploration", "Astronomy"],
            "difficulty": "Intermediate",
            "read_time": 9,
            "author": "Dr. Amanda Foster",
            "created_at": "2024-02-15"
        },
        
        # Business Content
        {
            "id": "11",
            "title": "Digital Marketing Strategies",
            "content": "Digital marketing encompasses all marketing efforts that use electronic devices or the internet. Key strategies include search engine optimization, content marketing, social media marketing, email marketing, and pay-per-click advertising.",
            "category": "Business",
            "tags": ["Marketing", "Digital", "SEO", "Social Media"],
            "difficulty": "Beginner",
            "read_time": 8,
            "author": "Sarah Mitchell",
            "created_at": "2024-01-12"
        },
        {
            "id": "12",
            "title": "Startup Funding and Venture Capital",
            "content": "Startup funding involves raising capital to grow a new business. Common sources include bootstrapping, angel investors, venture capital, crowdfunding, and bank loans. Each funding stage has different requirements and implications.",
            "category": "Business",
            "tags": ["Startup", "Funding", "Venture Capital", "Investment"],
            "difficulty": "Intermediate",
            "read_time": 11,
            "author": "James Wilson",
            "created_at": "2024-01-28"
        },
        {
            "id": "13",
            "title": "Project Management Methodologies",
            "content": "Project management methodologies provide structured approaches to planning, executing, and completing projects. Popular methodologies include Waterfall, Agile, Scrum, Kanban, and Lean, each suited for different project types and organizational cultures.",
            "category": "Business",
            "tags": ["Project Management", "Agile", "Scrum", "Methodology"],
            "difficulty": "Intermediate",
            "read_time": 9,
            "author": "Rachel Green",
            "created_at": "2024-02-03"
        },
        {
            "id": "14",
            "title": "Financial Planning and Investment",
            "content": "Financial planning involves setting financial goals and creating strategies to achieve them. Key components include budgeting, saving, investing, insurance, and retirement planning. Diversification and risk management are crucial for long-term success.",
            "category": "Business",
            "tags": ["Finance", "Investment", "Planning", "Retirement"],
            "difficulty": "Beginner",
            "read_time": 10,
            "author": "Michael Brown",
            "created_at": "2024-02-18"
        },
        {
            "id": "15",
            "title": "Leadership and Team Management",
            "content": "Effective leadership involves inspiring and guiding individuals or teams toward achieving common goals. Key skills include communication, decision-making, delegation, conflict resolution, and emotional intelligence.",
            "category": "Business",
            "tags": ["Leadership", "Management", "Team", "Communication"],
            "difficulty": "Intermediate",
            "read_time": 8,
            "author": "Linda Davis",
            "created_at": "2024-02-22"
        },
        
        # Health Content
        {
            "id": "16",
            "title": "Nutrition and Healthy Eating",
            "content": "Proper nutrition is essential for maintaining good health and preventing chronic diseases. A balanced diet includes fruits, vegetables, whole grains, lean proteins, and healthy fats while limiting processed foods, sugar, and excessive sodium.",
            "category": "Health",
            "tags": ["Nutrition", "Diet", "Healthy Eating", "Wellness"],
            "difficulty": "Beginner",
            "read_time": 6,
            "author": "Dr. Maria Garcia",
            "created_at": "2024-01-14"
        },
        {
            "id": "17",
            "title": "Mental Health and Stress Management",
            "content": "Mental health encompasses emotional, psychological, and social well-being. Effective stress management techniques include regular exercise, meditation, adequate sleep, social support, and professional counseling when needed.",
            "category": "Health",
            "tags": ["Mental Health", "Stress", "Wellness", "Psychology"],
            "difficulty": "Beginner",
            "read_time": 7,
            "author": "Dr. Kevin Adams",
            "created_at": "2024-01-30"
        },
        {
            "id": "18",
            "title": "Exercise and Physical Fitness",
            "content": "Regular physical activity is crucial for maintaining health and preventing disease. Effective fitness routines combine cardiovascular exercise, strength training, and flexibility work. The WHO recommends at least 150 minutes of moderate exercise weekly.",
            "category": "Health",
            "tags": ["Exercise", "Fitness", "Health", "Physical Activity"],
            "difficulty": "Beginner",
            "read_time": 8,
            "author": "Dr. Jennifer White",
            "created_at": "2024-02-06"
        },
        {
            "id": "19",
            "title": "Sleep Science and Better Sleep Habits",
            "content": "Quality sleep is essential for physical health, mental well-being, and cognitive function. Good sleep hygiene includes maintaining consistent sleep schedules, creating a comfortable sleep environment, and avoiding caffeine and screens before bedtime.",
            "category": "Health",
            "tags": ["Sleep", "Health", "Wellness", "Science"],
            "difficulty": "Beginner",
            "read_time": 6,
            "author": "Dr. Thomas Miller",
            "created_at": "2024-02-10"
        },
        {
            "id": "20",
            "title": "Preventive Medicine and Health Screening",
            "content": "Preventive medicine focuses on preventing diseases before they occur through vaccinations, regular health screenings, lifestyle modifications, and early detection strategies. Regular check-ups can identify risk factors and health issues early.",
            "category": "Health",
            "tags": ["Prevention", "Medicine", "Screening", "Healthcare"],
            "difficulty": "Intermediate",
            "read_time": 9,
            "author": "Dr. Susan Taylor",
            "created_at": "2024-02-20"
        },
        
        # Education Content
        {
            "id": "21",
            "title": "Online Learning and Educational Technology",
            "content": "Online learning has transformed education by making it more accessible and flexible. Educational technologies include learning management systems, interactive multimedia, virtual reality, and AI-powered personalized learning platforms.",
            "category": "Education",
            "tags": ["Online Learning", "EdTech", "Education", "Technology"],
            "difficulty": "Beginner",
            "read_time": 7,
            "author": "Prof. Nancy Clark",
            "created_at": "2024-01-16"
        },
        {
            "id": "22",
            "title": "Critical Thinking and Problem Solving",
            "content": "Critical thinking involves analyzing information objectively and making reasoned judgments. It includes skills like questioning assumptions, evaluating evidence, identifying biases, and considering alternative perspectives before reaching conclusions.",
            "category": "Education",
            "tags": ["Critical Thinking", "Problem Solving", "Learning", "Skills"],
            "difficulty": "Intermediate",
            "read_time": 8,
            "author": "Dr. Richard Moore",
            "created_at": "2024-01-26"
        },
        {
            "id": "23",
            "title": "Study Techniques and Learning Strategies",
            "content": "Effective study techniques improve learning retention and understanding. Research-backed methods include spaced repetition, active recall, the Feynman technique, mind mapping, and interleaving different subjects or topics.",
            "category": "Education",
            "tags": ["Study Skills", "Learning", "Memory", "Techniques"],
            "difficulty": "Beginner",
            "read_time": 6,
            "author": "Dr. Helen Anderson",
            "created_at": "2024-02-04"
        },
        {
            "id": "24",
            "title": "STEM Education and Career Paths",
            "content": "STEM education (Science, Technology, Engineering, Mathematics) provides students with skills needed for the modern workforce. Career paths in STEM are diverse and growing, offering opportunities in research, innovation, and problem-solving across industries.",
            "category": "Education",
            "tags": ["STEM", "Career", "Science", "Technology", "Engineering"],
            "difficulty": "Beginner",
            "read_time": 9,
            "author": "Prof. Daniel Lewis",
            "created_at": "2024-02-14"
        },
        {
            "id": "25",
            "title": "Language Learning and Cognitive Benefits",
            "content": "Learning a second language provides cognitive benefits including improved memory, enhanced problem-solving skills, and increased creativity. Effective language learning combines vocabulary building, grammar study, conversation practice, and cultural immersion.",
            "category": "Education",
            "tags": ["Language Learning", "Cognitive", "Brain", "Skills"],
            "difficulty": "Beginner",
            "read_time": 8,
            "author": "Dr. Patricia Robinson",
            "created_at": "2024-02-25"
        }
    ]
    
    # Add more content to reach 100+ items
    additional_topics = [
        ("Artificial Intelligence Ethics", "Technology", ["AI", "Ethics", "Philosophy", "Technology"]),
        ("Data Privacy and GDPR", "Technology", ["Privacy", "Data", "GDPR", "Security"]),
        ("IoT and Smart Cities", "Technology", ["IoT", "Smart Cities", "Innovation", "Technology"]),
        ("Microservices Architecture", "Technology", ["Architecture", "Software", "Development", "Scalability"]),
        ("DevOps and Continuous Integration", "Technology", ["DevOps", "CI/CD", "Development", "Automation"]),
        ("Oceanography and Marine Biology", "Science", ["Ocean", "Marine", "Biology", "Environment"]),
        ("Nanotechnology Applications", "Science", ["Nanotechnology", "Materials", "Innovation", "Science"]),
        ("Astronomy and Exoplanets", "Science", ["Astronomy", "Space", "Planets", "Discovery"]),
        ("Bioinformatics and Genomics", "Science", ["Bioinformatics", "Genomics", "Data", "Biology"]),
        ("Sustainable Agriculture", "Science", ["Agriculture", "Sustainability", "Food", "Environment"]),
        ("E-commerce and Online Business", "Business", ["E-commerce", "Online", "Business", "Digital"]),
        ("Supply Chain Management", "Business", ["Supply Chain", "Logistics", "Management", "Operations"]),
        ("Customer Experience Design", "Business", ["CX", "Design", "Customer", "Experience"]),
        ("Business Analytics and Data", "Business", ["Analytics", "Data", "Business Intelligence", "Metrics"]),
        ("Corporate Social Responsibility", "Business", ["CSR", "Ethics", "Sustainability", "Corporate"]),
        ("Immunology and Vaccines", "Health", ["Immunology", "Vaccines", "Health", "Medicine"]),
        ("Telemedicine and Digital Health", "Health", ["Telemedicine", "Digital Health", "Technology", "Healthcare"]),
        ("Pediatric Health and Development", "Health", ["Pediatrics", "Children", "Development", "Health"]),
        ("Geriatrics and Aging", "Health", ["Geriatrics", "Aging", "Elderly", "Health"]),
        ("Pharmacology and Drug Development", "Health", ["Pharmacology", "Drugs", "Medicine", "Research"]),
        ("Pedagogy and Teaching Methods", "Education", ["Pedagogy", "Teaching", "Methods", "Education"]),
        ("Special Education and Inclusion", "Education", ["Special Education", "Inclusion", "Disabilities", "Learning"]),
        ("Educational Psychology", "Education", ["Psychology", "Learning", "Education", "Behavior"]),
        ("Curriculum Development", "Education", ["Curriculum", "Development", "Education", "Design"]),
        ("Assessment and Evaluation", "Education", ["Assessment", "Evaluation", "Testing", "Education"])
    ]
    
    # Generate additional content
    for i, (title, category, tags) in enumerate(additional_topics, 26):
        content_data.append({
            "id": str(i),
            "title": title,
            "content": f"This is detailed content about {title.lower()}. It covers important concepts, practical applications, and current trends in the field. The content is designed to be informative and accessible to readers with varying levels of expertise.",
            "category": category,
            "tags": tags,
            "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
            "read_time": random.randint(5, 15),
            "author": f"Expert Author {i}",
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        })
    
    # Add more diverse content to reach 100+
    extended_topics = [
        "Robotics and Automation", "Virtual Reality Applications", "5G Technology Impact",
        "Edge Computing", "Computer Vision", "Natural Language Processing",
        "Biodiversity Conservation", "Renewable Energy Storage", "Climate Adaptation",
        "Evolutionary Biology", "Neuroscience Research", "Materials Science",
        "Digital Transformation", "Agile Methodology", "Brand Management",
        "Market Research", "Innovation Management", "Business Strategy",
        "Nutrition Science", "Public Health", "Medical Imaging",
        "Rehabilitation Medicine", "Health Economics", "Epidemiology",
        "Adult Learning", "Educational Leadership", "Inclusive Education",
        "Learning Disabilities", "Gifted Education", "Teacher Training"
    ]
    
    for i, topic in enumerate(extended_topics, 51):
        category = random.choice(["Technology", "Science", "Business", "Health", "Education"])
        content_data.append({
            "id": str(i),
            "title": topic,
            "content": f"Comprehensive overview of {topic.lower()} including key principles, methodologies, and real-world applications. This content explores current research, best practices, and future directions in the field.",
            "category": category,
            "tags": topic.split() + [category.lower()],
            "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
            "read_time": random.randint(4, 12),
            "author": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}",
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")
        })
    
    return content_data

def save_sample_data():
    """Save sample data to JSON file."""
    content = generate_sample_content()
    
    with open('/Users/ahmedrazakhan/Workspace/AI Projects/keyword-based-content-recommender/data/sample_content.json', 'w') as f:
        json.dump(content, f, indent=2)
    
    print(f"Generated {len(content)} content items")
    return content

if __name__ == "__main__":
    save_sample_data()