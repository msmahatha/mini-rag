#!/usr/bin/env python3
"""
Script to create a sample PDF for testing the Mini RAG application.
"""

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    def create_sample_pdf():
        filename = "sample_document.pdf"
        
        # Create a new PDF with reportlab
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, "Sample Document for RAG Testing")
        
        # Add content
        c.setFont("Helvetica", 12)
        y_position = height - 120
        
        content = [
            "Introduction to Artificial Intelligence",
            "",
            "Artificial Intelligence (AI) is a branch of computer science that aims to create",
            "systems capable of performing tasks that typically require human intelligence.",
            "These tasks include learning, reasoning, problem-solving, perception, and",
            "language understanding.",
            "",
            "Machine Learning",
            "",
            "Machine Learning is a subset of AI that enables computers to learn and improve",
            "from experience without being explicitly programmed. It uses algorithms to",
            "analyze data, identify patterns, and make predictions or decisions.",
            "",
            "Deep Learning",
            "",
            "Deep Learning is a specialized subset of machine learning that uses neural",
            "networks with multiple layers to model and understand complex patterns in data.",
            "It has been particularly successful in image recognition, natural language",
            "processing, and speech recognition.",
            "",
            "Applications of AI",
            "",
            "AI has numerous applications across various industries:",
            "- Healthcare: Diagnosis assistance and drug discovery",
            "- Finance: Fraud detection and algorithmic trading",
            "- Transportation: Autonomous vehicles and traffic optimization",
            "- Education: Personalized learning and intelligent tutoring systems",
            "- Entertainment: Recommendation systems and content generation",
        ]
        
        for line in content:
            if line.strip() == "":
                y_position -= 12
            else:
                if line in ["Machine Learning", "Deep Learning", "Applications of AI"]:
                    c.setFont("Helvetica-Bold", 12)
                else:
                    c.setFont("Helvetica", 12)
                
                c.drawString(72, y_position, line)
                y_position -= 15
                
                if y_position < 72:  # Start new page if needed
                    c.showPage()
                    y_position = height - 72
        
        c.save()
        print(f"Created {filename} successfully!")
        
    if __name__ == "__main__":
        create_sample_pdf()

except ImportError:
    print("reportlab not available. Creating a simple text alternative...")
    
    # Create a simple text file as fallback
    content = """Sample Document for RAG Testing

Introduction to Artificial Intelligence

Artificial Intelligence (AI) is a branch of computer science that aims to create systems capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.

Machine Learning

Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions or decisions.

Deep Learning

Deep Learning is a specialized subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data. It has been particularly successful in image recognition, natural language processing, and speech recognition.

Applications of AI

AI has numerous applications across various industries:
- Healthcare: Diagnosis assistance and drug discovery
- Finance: Fraud detection and algorithmic trading  
- Transportation: Autonomous vehicles and traffic optimization
- Education: Personalized learning and intelligent tutoring systems
- Entertainment: Recommendation systems and content generation
"""
    
    with open("sample_document_for_pdf_test.txt", "w") as f:
        f.write(content)
    
    print("Created sample_document_for_pdf_test.txt as a text alternative.")
    print("You can use any existing PDF file to test the PDF functionality.")
