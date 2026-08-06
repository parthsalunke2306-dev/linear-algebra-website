# Linear Algebra & Field Theory Explorer

An interactive, web-based Data Science & Linear Algebra learning platform featuring step-by-step LaTeX matrix solvers, 3D vector graphics, Galois Field $F_2$ arithmetic, secure user authentication, and persistent Supabase PostgreSQL database integration.

---

## 🌟 Live Demo & Deployment
- ⚡ **Live Production Application**: [https://linear-algebra-website.vercel.app](https://linear-algebra-website.vercel.app)
- 🐙 **GitHub Repository**: [https://github.com/parthsalunke2306-dev/linear-algebra-website.git](https://github.com/parthsalunke2306-dev/linear-algebra-website.git)

---

## 🚀 Key Features

### 🔐 1. Authentication & Security System
- **User Registration & Sign In**: Secure user signup, login, and password reset flows.
- **Server-Side Protected Routes**: All 6 mathematical solver tools are protected by `@login_required` decorators. Direct URL bypass is strictly prevented.
- **CSRF & SSL Protection**: Configured with `SECURE_PROXY_SSL_HEADER` and dynamic Vercel trusted origins for HTTPS and mobile browsers.

### 🧮 2. Data Science & Linear Algebra Modules
- **Unit 1.1: Gaussian Elimination & Row Operations**: Step-by-step REF & RREF reduction with LaTeX matrix formatting.
- **Unit 1.2: Field Axioms via GF(2)**: Galois Field $F_2 = \{0, 1\}$ addition and multiplication tables mod 2.
- **Unit 1.3: Vector Dot Product, Cross Product & Projections**: 3D vector calculations and interactive 3D orbit visualizer.
- **Unit 2.1: Gram–Schmidt Orthogonalization Process**: Vector basis orthogonalization and orthonormalization.
- **Unit 2.2: Cofactor Expansion for Determinants**: Matrix determinant calculation using sign checkerboards.
- **Unit 2.3: Eigenvalues, Eigenvectors & Diagonalization**: Characteristic polynomials, eigenspaces, and matrix decomposition $A = PDP^{-1}$.

### 💾 3. Database & Persistence Architecture
- **Supabase PostgreSQL**: Production data persistence for user accounts, matrix calculation logs, and saved presets.
- **Signed Cookie Session Resilience**: Cryptographically signed cookie session fallback for serverless cloud environments.

---

## ⚙️ Local Setup Instructions

1. **Clone Repository**:
   ```bash
   git clone https://github.com/parthsalunke2306-dev/linear-algebra-website.git
   cd linear-algebra-website
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate # On macOS/Linux
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations & Start Local Server**:
   ```bash
   python manage.py migrate
   python manage.py runserver 8000
   ```

5. Access the app locally at `http://127.0.0.1:8000`.
