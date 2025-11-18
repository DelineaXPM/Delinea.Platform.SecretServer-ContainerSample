// MongoDB initialization script
// This script will be executed when the MongoDB container starts

// Switch to the employee database
db = db.getSiblingDB('admin');

// Create a dedicated application user with limited permissions
// These credentials should match what's stored in your Delinea Secret Server
db.createUser({
  user: "myuser",
  pwd: "mypassword1234", // This will be replaced by Delinea credentials
  roles: [
    { role: "readWrite", db: "company_db" }  // Only read/write access to data
  ]
});

print("Created application user: app_user with readWrite permissions on company_db");

// Switch to the company_db database
db = db.getSiblingDB('company_db');

// Create employees collection with sample data
db.employees.insertMany([
  {
    name: "John Smith",
    position: "Software Engineer",
    department: "Engineering",
    email: "john.smith@company.com",
    salary: 75000,
    startDate: "2023-01-15",
    status: "active",
    skills: ["JavaScript", "Node.js", "MongoDB"],
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    name: "Sarah Johnson",
    position: "Senior Developer",
    department: "Engineering",
    email: "sarah.johnson@company.com",
    salary: 95000,
    startDate: "2022-03-10",
    status: "active",
    skills: ["Python", "React", "AWS"],
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    name: "Mike Chen",
    position: "Product Manager",
    department: "Product",
    email: "mike.chen@company.com",
    salary: 110000,
    startDate: "2021-08-20",
    status: "active",
    skills: ["Product Strategy", "Analytics", "Scrum"],
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    name: "Emily Davis",
    position: "UX Designer",
    department: "Design",
    email: "emily.davis@company.com",
    salary: 70000,
    startDate: "2023-05-01",
    status: "active",
    skills: ["Figma", "User Research", "Prototyping"],
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    name: "David Wilson",
    position: "DevOps Engineer",
    department: "Engineering",
    email: "david.wilson@company.com",
    salary: 85000,
    startDate: "2022-11-15",
    status: "active",
    skills: ["Docker", "Kubernetes", "Terraform"],
    createdAt: new Date(),
    updatedAt: new Date()
  },
  {
    name: "Lisa Brown",
    position: "Data Scientist",
    department: "Analytics",
    email: "lisa.brown@company.com",
    salary: 90000,
    startDate: "2023-02-20",
    status: "active",
    skills: ["Python", "Machine Learning", "SQL"],
    createdAt: new Date(),
    updatedAt: new Date()
  }
]);

// Create indexes for better performance
db.employees.createIndex({ "email": 1 }, { unique: true });
db.employees.createIndex({ "department": 1 });
db.employees.createIndex({ "status": 1 });
db.employees.createIndex({ "startDate": 1 });

// Create a departments collection for reference
db.departments.insertMany([
  {
    name: "Engineering",
    description: "Software development and technical operations",
    manager: "John Smith",
    budget: 500000,
    createdAt: new Date()
  },
  {
    name: "Product",
    description: "Product strategy and management",
    manager: "Mike Chen",
    budget: 200000,
    createdAt: new Date()
  },
  {
    name: "Design",
    description: "User experience and interface design",
    manager: "Emily Davis",
    budget: 150000,
    createdAt: new Date()
  },
  {
    name: "Analytics",
    description: "Data analysis and business intelligence",
    manager: "Lisa Brown",
    budget: 300000,
    createdAt: new Date()
  }
]);

// Print initialization status
print("Employee database initialized successfully!");
print("Created collections: employees, departments");
print("Inserted " + db.employees.count() + " employees");
print("Inserted " + db.departments.count() + " departments");
print("Database initialization complete.");
