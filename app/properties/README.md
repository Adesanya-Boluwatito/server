Sure! Below is a detailed README file that explains how to integrate the provided Flask routes for managing properties with a React frontend application. This README includes the Flask backend setup, API endpoint details, and usage instructions in a React application.

---

# Property Management API

## Overview

This API allows for the management of property listings, including creating, updating, deleting, and searching for properties. It uses Flask as the backend framework and integrates with Firebase Storage for handling property images.

## Flask Backend Setup

### Prerequisites

- Python 3.x
- Flask
- Flask-Login
- SQLAlchemy
- Google Cloud Storage library
- Firebase credentials
- PostgreSQL (or any other SQL database supported by SQLAlchemy)

### Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Set Up a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   - Set up environment variables for database configuration and Firebase credentials.
   - Example:

     ```bash
     export DATABASE_URL="your_database_url"
     export FIREBASE_CONFIG="path_to_your_firebase_credentials.json"
     export CA_PEM="path_to_your_ca_certificate.pem"
     ```

5. **Run Database Migrations**

   ```bash
   flask db upgrade
   ```

6. **Run the Flask Application**

   ```bash
   flask run
   ```

### API Endpoints

#### 1. Create Property

- **Endpoint**: `/property/new_property/<realtor_id>`
- **Method**: POST
- **Headers**: `Content-Type: application/json` or `multipart/form-data`
- **Authorization**: Requires user to be logged in
- **Request Body**:

  ```json
  {
    "location": "Location",
    "description": "Description",
    "address": "Address",
    "bedrooms": 3,
    "bathrooms": 2,
    "title": "Title",
    "category": "Category",
    "price": 100000,
    "property_type": "Property Type",
    "size": 1500,
    "file": "file"  // multipart/form-data
  }
  ```

- **Response**: Returns the created property in JSON format

#### 2. Get All Properties

- **Endpoint**: `/property/all_properties`
- **Method**: GET
- **Request Params**:

  ```json
  {
    "page": 1 // Optional, default is 1
  }
  ```

- **Response**: Returns a paginated list of properties with images in JSON format

#### 3. Get Property by ID

- **Endpoint**: `/property/<property_id>`
- **Method**: GET
- **Response**: Returns the property details in JSON format

#### 4. Update Property Availability

- **Endpoint**: `/property/update_property_availability/<realtor_id>/<property_id>`
- **Method**: PATCH
- **Request Body**:

  ```json
  {
    "action": "activate" // or "deactivate"
  }
  ```

- **Response**: Returns a success message in JSON format

#### 5. Update Property

- **Endpoint**: `/property/update_property/<realtor_id>/<property_id>`
- **Method**: PATCH
- **Headers**: `Content-Type: application/json` or `multipart/form-data`
- **Request Body**:

  ```json
  {
    "location": "New Location",
    "description": "New Description",
    "address": "New Address",
    "bedrooms": 4,
    "bathrooms": 3,
    "title": "New Title",
    "category": "New Category",
    "price": 150000,
    "property_type": "New Property Type",
    "size": 2000,
    "file": "file"  // multipart/form-data
  }
  ```

- **Response**: Returns a success message in JSON format

#### 6. Delete Property

- **Endpoint**: `/property/delete_property/<realtor_id>/<property_id>`
- **Method**: DELETE
- **Response**: Returns a success message in JSON format

#### 7. Search Properties

- **Endpoint**: `/property/search_properties`
- **Method**: GET
- **Request Params**:

  ```json
  {
    "search_term": "Location or Description",
    "min_price": 50000,
    "max_price": 200000,
    "bedrooms": 3,
    "bathrooms": 2,
    "category": "Category",
    "property_type": "Property Type",
    "max_area": 2000,
    "page": 1 // Optional, default is 1
  }
  ```

- **Response**: Returns a list of properties matching the search criteria in JSON format

#### 8. Get Recently Added Properties

- **Endpoint**: `/property/recently_added`
- **Method**: GET
- **Response**: Returns a list of the four most recently added properties in JSON format

## React Frontend Integration

### Prerequisites

- Node.js and npm
- React

### Installation

1. **Create a React App**

   ```bash
   npx create-react-app property-management
   cd property-management
   ```

2. **Install Axios for API Requests**

   ```bash
   npm install axios
   ```

3. **Create API Service**

   Create a new file `apiService.js` in the `src` directory and add the following code:

   ```javascript
   import axios from 'axios';

   const apiClient = axios.create({
       baseURL: 'http://localhost:5000',
       withCredentials: true
   });

   export const createProperty = async (realtorId, propertyData) => {
       const formData = new FormData();
       for (const key in propertyData) {
           formData.append(key, propertyData[key]);
       }
       const response = await apiClient.post(`/property/new_property/${realtorId}`, formData, {
           headers: { 'Content-Type': 'multipart/form-data' }
       });
       return response.data;
   };

   export const getAllProperties = async (page = 1) => {
       const response = await apiClient.get(`/property/all_properties?page=${page}`);
       return response.data;
   };

   export const getPropertyById = async (propertyId) => {
       const response = await apiClient.get(`/property/${propertyId}`);
       return response.data;
   };

   export const updatePropertyAvailability = async (realtorId, propertyId, action) => {
       const response = await apiClient.patch(`/property/update_property_availability/${realtorId}/${propertyId}`, { action });
       return response.data;
   };

   export const updateProperty = async (realtorId, propertyId, propertyData) => {
       const formData = new FormData();
       for (const key in propertyData) {
           formData.append(key, propertyData[key]);
       }
       const response = await apiClient.patch(`/property/update_property/${realtorId}/${propertyId}`, formData, {
           headers: { 'Content-Type': 'multipart/form-data' }
       });
       return response.data;
   };

   export const deleteProperty = async (realtorId, propertyId) => {
       const response = await apiClient.delete(`/property/delete_property/${realtorId}/${propertyId}`);
       return response.data;
   };

   export const searchProperties = async (searchParams) => {
       const response = await apiClient.get('/property/search_properties', { params: searchParams });
       return response.data;
   };

   export const getRecentlyAddedProperties = async () => {
       const response = await apiClient.get('/property/recently_added');
       return response.data;
   };
   ```

4. **Create React Components**

   Create a new directory `components` in the `src` directory and add the following files:

   - `CreateProperty.js`:

     ```javascript
     import React, { useState } from 'react';
     import { createProperty } from '../apiService';

     const CreateProperty = ({ realtorId }) => {
         const [formData, setFormData] = useState({
             location: '',
             description: '',
             address: '',
             bedrooms: '',
             bathrooms: '',
             title: '',
             category: '',
             price: '',
             property_type: '',
             size: '',
             file: null
         });

         const handleChange = (e) => {
             const { name, value, files } = e.target;
             setFormData((prevData) => ({
                 ...prevData,
                 [name]: files ? files[0] : value
             }));
         };

         const handleSubmit = async (e) => {
             e.preventDefault();
             try {
                 const response = await createProperty(realtorId, formData);
                 console.log('Property created successfully:', response);
             } catch (error) {
                 console.error('Error creating property:', error);
             }
         };

         return (
             <form onSubmit={handleSubmit}>
                 <input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="Location" required />
                 <textarea name="description" value={formData.description} onChange={handleChange} placeholder="Description" required />
                 <input type="

text" name="address" value={formData.address} onChange={handleChange} placeholder="Address" required />
                 <input type="number" name="bedrooms" value={formData.bedrooms} onChange={handleChange} placeholder="Bedrooms" required />
                 <input type="number" name="bathrooms" value={formData.bathrooms} onChange={handleChange} placeholder="Bathrooms" required />
                 <input type="text" name="title" value={formData.title} onChange={handleChange} placeholder="Title" required />
                 <input type="text" name="category" value={formData.category} onChange={handleChange} placeholder="Category" required />
                 <input type="number" name="price" value={formData.price} onChange={handleChange} placeholder="Price" required />
                 <input type="text" name="property_type" value={formData.property_type} onChange={handleChange} placeholder="Property Type" required />
                 <input type="number" name="size" value={formData.size} onChange={handleChange} placeholder="Size" required />
                 <input type="file" name="file" onChange={handleChange} required />
                 <button type="submit">Create Property</button>
             </form>
         );
     };

     export default CreateProperty;
     ```

   - `PropertyList.js`:

     ```javascript
     import React, { useEffect, useState } from 'react';
     import { getAllProperties } from '../apiService';

     const PropertyList = () => {
         const [properties, setProperties] = useState([]);
         const [page, setPage] = useState(1);

         useEffect(() => {
             const fetchProperties = async () => {
                 try {
                     const response = await getAllProperties(page);
                     setProperties(response.properties);
                 } catch (error) {
                     console.error('Error fetching properties:', error);
                 }
             };

             fetchProperties();
         }, [page]);

         return (
             <div>
                 <ul>
                     {properties.map((property) => (
                         <li key={property.id}>
                             <p>{property.title}</p>
                             <img src={property.property_images[0]?.storage_url} alt={property.title} />
                         </li>
                     ))}
                 </ul>
                 <button onClick={() => setPage((prev) => prev + 1)}>Next Page</button>
             </div>
         );
     };

     export default PropertyList;
     ```

5. **Use Components in App**

   Replace the content of `App.js` with:

   ```javascript
   import React from 'react';
   import CreateProperty from './components/CreateProperty';
   import PropertyList from './components/PropertyList';

   const App = () => {
       const realtorId = "your_realtor_id";  // Replace with the actual realtor ID

       return (
           <div>
               <h1>Property Management</h1>
               <CreateProperty realtorId={realtorId} />
               <PropertyList />
           </div>
       );
   };

   export default App;
   ```

### Running the Application

1. **Start the Flask Backend**

   ```bash
   flask run
   ```

2. **Start the React Frontend**

   ```bash
   npm start
   ```

3. **Access the Application**

   Open your web browser and navigate to `http://localhost:3000` to interact with the property management application.

### Summary

This README file provides detailed instructions on setting up and using a Flask backend for managing property listings and integrating it with a React frontend application. It includes API endpoint details, usage examples, and React component implementations for seamless interaction with the Flask API.

