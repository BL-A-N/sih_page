const express = require('express');
const { MongoClient } = require('mongodb');
const path = require('path');
const cors = require("cors");

const app = express();
const port = 3000;

// MongoDB connection string
const uri = "mongodb+srv://4n122104_db_user:penguins@cluster0.w4uqzla.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";

// Cached MongoClient instance
let cachedClient = null;

async function connectToDatabase() {
  if (cachedClient && cachedClient.topology && cachedClient.topology.isConnected()) {
    return cachedClient;
  }
  const client = new MongoClient(uri);
  cachedClient = await client.connect();
  return cachedClient;
}

app.use(cors({
  origin: "*",
}));

// Middleware to serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Middleware to parse JSON bodies. This needs to be before the routes are defined.
app.use(express.json());

// Redirect the root URL to your main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Route for individual product pages
app.get('/product/:itemId', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const getProductsCollection = async () => {
  const client = await connectToDatabase();
  const db = client.db("your_catalogue_db");
  return db.collection("products");
};

// API endpoint to fetch products
app.get('/api/products', async (req, res) => {
    try {
        const productsCollection = await getProductsCollection();
        const products = await productsCollection.find({}).toArray();
        res.json(products);
    } catch (err) {
        console.error("Error fetching products:", err);
        res.status(500).send("Error fetching products.");
    }
});

// API endpoint to add a new product
app.post('/api/products', async (req, res) => {
  try {
    const productsCollection = await getProductsCollection();
    const newProduct = req.body;
    // The user's email is now sent from the frontend
    const result = await productsCollection.insertOne(newProduct);
    if (result.acknowledged) {
      res.status(201).json(newProduct);
    } else {
      res.status(500).send("Failed to add product.");
    }
  } catch (err) {
    console.error("Error adding product:", err);
    res.status(500).send("Error adding product.");
  }
});

// API endpoint to delete a product
app.delete('/api/products/:itemId', async (req, res) => {
  try {
    const productsCollection = await getProductsCollection();
    const { itemId } = req.params;
    const result = await productsCollection.deleteOne({ itemId: itemId });

    if (result.deletedCount === 1) {
      res.status(200).json({ message: 'Product deleted successfully' });
    } else {
      res.status(404).send('Product not found');
    }
  } catch (err) {
    console.error("Error deleting product:", err);
    res.status(500).send("Error deleting product.");
  }
});

// For local development, you can still use app.listen
if (process.env.NODE_ENV !== 'production') {
  app.listen(port, () => console.log(`Server running at http://localhost:${port}`));
}

module.exports = app;
