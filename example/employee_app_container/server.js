require('dotenv').config();
const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');
const path = require('path');
const cors = require('cors');
// importing sidecar secrets function
const { getSecretFromDelineaSidecar } = require('./DelineaSidecarHelper');

const app = express();

// Configuration from environment variables
const config = {
  port: process.env.APP_PORT || 3000,
  appName: process.env.APP_NAME || 'Employee Management System',
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || '27017',
    name: process.env.DB_NAME || 'company_db',
    username: process.env.DB_USERNAME || 'admin',
    password: process.env.DB_PASSWORD || 'password123',
    authSource: process.env.DB_AUTH_SOURCE || 'admin'
  }
};

// Build MongoDB connection string from environment variables
const mongoUrl = `mongodb://${config.database.username}:${config.database.password}@${config.database.host}:${config.database.port}/${config.database.name}?authSource=${config.database.authSource}`;

console.log('🚀 Starting', config.appName);
console.log('📊 Dashboard will be available at: http://localhost:' + config.port);
console.log('🔗 Using Database:', config.database.host + ':' + config.database.port + '/' + config.database.name);
console.log('👤 Database User:', config.database.username);

let db;

// Connect to MongoDB
async function connectToDatabase() {
    try {
        console.log('🔄 Connecting to MongoDB...');

    //(start)changes for sidecar secrets
    const secret = await getSecretFromDelineaSidecar('11126');
    // OR
    // const secret = await getSecretFromDelineaSidecar('mongo-secret');
        console.log('🔐 Retrieved MongoDB secret from sidecar :', secret);
        if (secret.username) {
                config.database.username = secret.username;
            }
            if (secret.password) {
                config.database.password = secret.password;
            }
			if (secret.database) {
                config.database.name = secret.database;
            }

        const mongoUrl = `mongodb://${config.database.username}:${config.database.password}@${config.database.host}:${config.database.port}/${config.database.name}?authSource=${config.database.authSource}`;
        console.log('🔗 Updated MongoDB connection string with sidecar secrets');
        //(end)changes for sidecar secrets

        const client = new MongoClient(mongoUrl);
        await client.connect();
        db = client.db(config.database.name);
        console.log('✅ Connected to MongoDB successfully');
        console.log('📂 Using pre-initialized database from init-db.js');
    } catch (error) {
        console.error('❌ MongoDB connection failed:', error.message);
        console.error('🔍 Connection details:', {
            host: config.database.host,
            port: config.database.port,
            database: config.database.name,
            user: config.database.username
        });
        process.exit(1);
    }
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/api/employees', async (req, res) => {
    try {
        const employees = await db.collection('employees').find({}).toArray();
        res.json({
            success: true,
            count: employees.length,
            data: employees,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error fetching employees:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch employees',
            message: error.message
        });
    }
});

app.get('/api/config', (req, res) => {
    res.json({
        appName: config.appName,
        environment: process.env.NODE_ENV || 'development',
        database: {
            host: config.database.host,
            port: config.database.port,
            name: config.database.name,
            user: config.database.username,
            // Don't expose password in API
            connected: db ? true : false
        },
        timestamp: new Date().toISOString()
    });
});

app.get('/api/health', async (req, res) => {
    try {
        // Check database connectivity
        await db.admin().ping();
        res.json({
            status: 'healthy',
            database: 'connected',
            timestamp: new Date().toISOString(),
            uptime: process.uptime()
        });
    } catch (error) {
        res.status(503).json({
            status: 'unhealthy',
            database: 'disconnected',
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

app.get('/api/status', (req, res) => {
    res.json({
        status: 'running',
        appName: config.appName,
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'development',
        timestamp: new Date().toISOString(),
        database: {
            connected: db ? true : false,
            host: config.database.host,
            name: config.database.name
        },
        message: 'Application running with environment-based configuration'
    });
});

// Update employee API endpoint
app.put('/api/employees/:id', async (req, res) => {
    try {
        const id = req.params.id;
        const update = req.body;
        // Remove empty salary if not provided
        if (!update.salary) delete update.salary;
        const result = await db.collection('employees').updateOne(
            { $or: [ { _id: ObjectId.isValid(id) ? new ObjectId(id) : id }, { id: Number(id) } ] },
            { $set: update }
        );
        if (result.matchedCount === 0) {
            return res.status(404).json({ success: false, error: 'Employee not found' });
        }
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Application Error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
});

// Start server
connectToDatabase().then(() => {
    app.listen(config.port, () => {
        console.log(`🌐 Server running on port ${config.port}`);
        console.log(`📊 Dashboard: http://localhost:${config.port}`);
        console.log(`🔗 API: http://localhost:${config.port}/api/employees`);
        console.log(`📈 Status: http://localhost:${config.port}/api/status`);
        console.log(`💚 Health: http://localhost:${config.port}/api/health`);
        console.log(`⚙️  Config: http://localhost:${config.port}/api/config`);
    });
}).catch(error => {
    console.error('Failed to start application:', error);
    process.exit(1);
});
