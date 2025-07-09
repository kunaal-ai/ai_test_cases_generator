"""
This module contains all templates for test case generation, including domain-specific,
feature-specific, and test-type-specific templates.
"""

# Domain-specific templates
DOMAIN_TEMPLATES = {
    "Fintech": """
    Additional considerations for Fintech testing:
    1. Financial Regulations and Compliance:
        - KYC/AML requirements
        - Financial data security standards
        - Transaction reporting requirements
        - Regional regulatory compliance
        - Audit trail requirements
    
    2. Transaction Processing:
        - Payment processing accuracy
        - Currency conversion
        - Fee calculations
        - Transaction limits
        - Multi-currency support
    
    3. Security and Fraud:
        - Fraud detection mechanisms
        - Transaction monitoring
        - Account security measures
        - Authentication protocols
        - Financial data encryption
    
    4. Integration Testing:
        - Payment gateway integration
        - Banking system interfaces
        - Credit scoring systems
        - Financial data providers
        - Regulatory reporting systems
    
    5. Data Accuracy:
        - Financial calculations
        - Interest computations
        - Balance tracking
        - Transaction history
        - Statement generation
    """,
    
    "Healthcare": """
    Additional considerations for Healthcare testing:
    1. Regulatory Compliance:
        - HIPAA compliance
        - FDA regulations
        - Clinical data protection
        - Patient privacy
        - Medical device standards
    
    2. Patient Data Management:
        - Electronic Health Records (EHR)
        - Patient identification
        - Medical history tracking
        - Prescription management
        - Appointment scheduling
    
    3. Clinical Workflows:
        - Patient care protocols
        - Medical device integration
        - Lab result processing
        - Diagnostic procedures
        - Treatment planning
    
    4. Security and Privacy:
        - PHI protection
        - Access control
        - Audit logging
        - Data encryption
        - Consent management
    
    5. Integration Testing:
        - Medical device integration
        - Lab system interfaces
        - Pharmacy systems
        - Insurance verification
        - Healthcare provider networks
    """,
    
    "E-commerce": """
    Additional considerations for E-commerce testing:
    1. Shopping Experience:
        - Product catalog management
        - Search and filtering
        - Shopping cart functionality
        - Checkout process
        - Order tracking
    
    2. Payment Processing:
        - Multiple payment methods
        - Payment gateway integration
        - Refund processing
        - Invoice generation
        - Tax calculations
    
    3. Inventory Management:
        - Stock tracking
        - Product variants
        - Warehouse management
        - Supply chain integration
        - Inventory alerts
    
    4. Customer Management:
        - User accounts
        - Wishlist functionality
        - Order history
        - Customer support
        - Reviews and ratings
    
    5. Security:
        - Payment security
        - Customer data protection
        - Fraud prevention
        - PCI compliance
        - Session management
    """,
    
    "Manufacturing": """
    Additional considerations for Manufacturing testing:
    1. Production Systems:
        - Manufacturing process control
        - Quality control systems
        - Equipment monitoring
        - Production scheduling
        - Resource management
    
    2. Supply Chain:
        - Inventory tracking
        - Supplier management
        - Material requirements planning
        - Warehouse operations
        - Shipping logistics
    
    3. Quality Assurance:
        - Product specifications
        - Quality metrics
        - Compliance tracking
        - Defect management
        - Inspection procedures
    
    4. Equipment Integration:
        - Machine control systems
        - Sensor data processing
        - Maintenance scheduling
        - Performance monitoring
        - Alert systems
    
    5. Regulatory Compliance:
        - Safety standards
        - Environmental regulations
        - Industry certifications
        - Documentation requirements
        - Audit trail
    """,
    
    "Education": """
    Additional considerations for Education testing:
    1. Learning Management:
        - Course management
        - Content delivery
        - Student progress tracking
        - Assessment systems
        - Grading functionality
    
    2. User Management:
        - Student profiles
        - Teacher accounts
        - Parent access
        - Administrative roles
        - Class management
    
    3. Content Delivery:
        - Multimedia support
        - Interactive content
        - Assignment submission
        - Resource management
        - Accessibility compliance
    
    4. Assessment:
        - Quiz/Test creation
        - Automated grading
        - Plagiarism detection
        - Performance analytics
        - Feedback mechanisms
    
    5. Integration:
        - Learning tool interoperability (LTI)
        - Student information systems
        - Library resources
        - Video conferencing
        - Authentication systems
    """
}

# Feature type specific templates
FEATURE_TEMPLATES = {
    "UI": """
    Additional considerations for UI testing:
    1. Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
    2. Responsive design (Mobile, Tablet, Desktop, Ultra-wide screens)
    3. UI element states (Enabled, Disabled, Hover, Focus, Active)
    4. Accessibility (WCAG compliance, Screen readers, Keyboard navigation)
    5. Input field validations (Boundary values, Special characters, XSS prevention)
    6. Layout and styling (RTL support, Dark/Light themes, Font scaling)
    7. Error states and messages
    8. Loading states and animations
    9. Browser storage handling
    10. Offline functionality
    """,
    "API": """
    Additional considerations for API testing:
    1. HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
    2. Request/Response validation (Headers, Body, Query params, Path params)
    3. Status codes (Success, Client errors, Server errors)
    4. Authentication (Basic, Bearer, OAuth, API keys)
    5. Authorization (Role-based access, Permissions)
    6. Rate limiting and throttling
    7. Request timeouts and retries
    8. API versioning
    9. Payload size limits
    10. CORS and security headers
    """,
    "Database": """
    Additional considerations for Database testing:
    1. CRUD operations with edge cases
    2. Data integrity (Constraints, Triggers, Cascading)
    3. Transaction management (Commit, Rollback, Deadlocks)
    4. Concurrent access and race conditions
    5. Data migration and versioning
    6. Backup and recovery scenarios
    7. Performance optimization (Indexing, Query plans)
    8. Data encryption and security
    9. Connection pooling and timeouts
    10. Data archival and cleanup
    """,
    "Mobile": """
    Additional considerations for Mobile testing:
    1. Platform specific behavior (iOS, Android)
    2. Device fragmentation (Screen sizes, OS versions)
    3. Network conditions (2G, 3G, 4G, 5G, Offline)
    4. Battery consumption and performance
    5. App lifecycle (Background, Foreground, Killed)
    6. Device permissions and settings
    7. Push notifications
    8. Local storage and caching
    9. App updates and migrations
    10. Integration with device features (Camera, GPS, Biometrics)
    """,
    "Integration": """
    Additional considerations for Integration testing:
    1. System dependencies and interfaces
    2. Data flow between components
    3. Error handling and recovery
    4. Service contracts and versioning
    5. Asynchronous operations
    6. Message queues and events
    7. External service mocking
    8. Configuration management
    9. Deployment scenarios
    10. Monitoring and logging
    """
}

# Test type specific templates
TEST_TEMPLATES = {
    "Smoke Testing": """
    Focus on critical path testing:
    1. Core functionality verification
    2. Basic navigation flows
    3. Critical business transactions
    4. Essential integrations
    5. Basic error handling
    Include quick verification of fundamental features.
    """,
    "End-to-End Testing": """
    Focus on complete business flows:
    1. Full user journeys and scenarios
    2. Cross-component interactions
    3. Data flow across systems
    4. Third-party integrations
    5. Error scenarios and recovery
    6. Edge cases and boundary conditions
    7. Different user roles and permissions
    8. Configuration variations
    9. Performance implications
    10. Security considerations
    """,
    "Performance Testing": """
    Focus on system performance:
    1. Response time benchmarks
    2. Load testing scenarios (Normal, Peak, Stress)
    3. Scalability verification
    4. Resource utilization (CPU, Memory, Network, Disk)
    5. Concurrency and parallel processing
    6. Caching effectiveness
    7. Database performance
    8. Network latency impact
    9. Third-party service performance
    10. Recovery time objectives
    """,
    "Regression Testing": """
    Focus on impact analysis:
    1. Existing functionality verification
    2. Integration points
    3. Common user flows
    4. Historical defect areas
    5. Configuration testing
    6. Cross-browser compatibility
    7. Database migrations
    8. API versioning
    9. Security compliance
    10. Performance baselines
    """,
    "Security Testing": """
    Focus on security aspects:
    1. Authentication mechanisms
    2. Authorization and access control
    3. Data encryption (In-transit, At-rest)
    4. Input validation and sanitization
    5. Common vulnerabilities (OWASP Top 10)
    6. Session management
    7. API security
    8. File upload/download security
    9. Audit logging
    10. Compliance requirements
    """,
    "Accessibility Testing": """
    Focus on accessibility compliance:
    1. Screen reader compatibility
    2. Keyboard navigation
    3. Color contrast and visibility
    4. Alternative text for images
    5. ARIA labels and roles
    6. Focus management
    7. Form field accessibility
    8. Error message announcements
    9. Document structure
    10. Multimedia accessibility
    """
}
