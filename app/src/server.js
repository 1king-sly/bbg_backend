const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const { PrismaClient } = require('@prisma/client');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
require('dotenv').config();

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Authentication middleware
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await prisma.user.findUnique({
      where: { email: decoded.email }
    });
    
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Auth routes
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user || !bcrypt.compareSync(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({ token, user: { id: user.id, email: user.email, role: user.role } });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// User routes
app.post('/api/users', async (req, res) => {
  const { email, name, password } = req.body;

  try {
    const hashedPassword = bcrypt.hashSync(password, 10);
    const user = await prisma.user.create({
      data: {
        email,
        name,
        password: hashedPassword
      }
    });

    const { password: _, ...userWithoutPassword } = user;
    res.status(201).json(userWithoutPassword);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/api/users/me', authenticateToken, async (req, res) => {
  const { password: _, ...userWithoutPassword } = req.user;
  res.json(userWithoutPassword);
});

app.put('/api/users/me', authenticateToken, async (req, res) => {
  const { name, phone, dateOfBirth } = req.body;

  try {
    const updatedUser = await prisma.user.update({
      where: { id: req.user.id },
      data: {
        name,
        phone,
        dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined
      }
    });

    const { password: _, ...userWithoutPassword } = updatedUser;
    res.json(userWithoutPassword);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Expert routes
app.post('/api/experts', authenticateToken, async (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Not authorized' });
  }

  const { name, email, phone, password, fieldOfExpertise } = req.body;

  try {
    const hashedPassword = bcrypt.hashSync(password, 10);
    const expert = await prisma.expert.create({
      data: {
        name,
        email,
        phone,
        password: hashedPassword,
        fieldOfExpertise
      }
    });

    const { password: _, ...expertWithoutPassword } = expert;
    res.status(201).json(expertWithoutPassword);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/api/experts/:id', authenticateToken, async (req, res) => {
  try {
    const expert = await prisma.expert.findUnique({
      where: { id: parseInt(req.params.id) }
    });

    if (!expert) {
      return res.status(404).json({ error: 'Expert not found' });
    }

    const { password: _, ...expertWithoutPassword } = expert;
    res.json(expertWithoutPassword);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Session routes
app.post('/api/sessions', authenticateToken, async (req, res) => {
  const { expertId, startTime, type } = req.body;

  try {
    const session = await prisma.session.create({
      data: {
        userId: req.user.id,
        expertId: parseInt(expertId),
        startTime: new Date(startTime),
        type,
        status: 'scheduled'
      },
      include: {
        expert: true
      }
    });

    res.status(201).json(session);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/api/sessions', authenticateToken, async (req, res) => {
  try {
    const sessions = await prisma.session.findMany({
      where: { userId: req.user.id },
      include: {
        expert: true
      }
    });

    res.json(sessions);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});