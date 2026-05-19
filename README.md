# Emergency Resource Allocation System (ERA)

A sophisticated web-based application built with **Django** to optimize inventory levels and streamline the logistics of essential life-saving resources during natural disasters and local emergencies.

## 🚨 Overview
The **Emergency Resource Allocation System** coordinates critical supplies (such as food, water, medical kits, and shelter) across multiple districts. It establishes a streamlined workflow that connects citizens needing aid, volunteers handling distribution, and district officers verifying resource levels.

---

## ✨ Key Modules

### 👑 Admin (System Administrator)
*   **District Management**: Configure geographical coverage areas.
*   **Officer Management**: Recruit and assign district officers to coordinate local stations.
*   **Resource Categorization**: Create and manage master lists of aid categories (e.g., Food, Water, Medicine, Shelter).
*   **Volunteer Approvals**: Review and onboard local volunteer responders.

### 👮 Staff (District Officers)
*   **Stock Inventory Control**: Manage local warehouse stock levels, add new inventory, and set safety thresholds.
*   **Aid Request Processing**: Review, verify, and approve incoming resource requests from local citizens.
*   **Volunteer Dispatch**: Formulate distribution tasks and assign deliveries to online volunteers.

### 🤝 Volunteer (Logistics Responders)
*   **Logistics Tracking**: View assigned resource delivery missions.
*   **Status Updates**: Provide real-time delivery status updates upon completion.

### 👤 Citizen (Community Members)
*   **Aid Requests**: Submit structured requests for essential resources indicating urgency levels and locations.
*   **Request History**: Track the review, verification, and dispatch progress of all requested aid.

---

## 🛠 Technology Stack
*   **Backend**: Python / Django Framework
*   **Frontend**: Responsive HTML5, Custom CSS Variables, Glassmorphic Dashboard Design, FontAwesome
*   **Database**: SQLite3 / Django ORM Compatibility
*   **Styling & UX**: Sleek gradients, vibrant badges, and premium dashboard widgets with smooth hover micro-animations.

---

## 🚀 Installation & Running

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/VishnuSuresh0204/Resource-Allocation-System-.git
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup & Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

---
*Developed to ensure critical resources reach those in need, quickly and transparently.*
