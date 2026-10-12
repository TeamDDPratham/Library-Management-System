# Deploying Library Management System to Vercel

This guide explains how to deploy your **Flask + MySQL Library Management System** to **Vercel**.

---

## 1. Important Architecture Concept: Cloud Database vs Local Database

- When running locally on your laptop, Flask connects to `localhost:3306` (`MySQL267` service on your PC).
- When deployed on **Vercel**, the application runs in Vercel's cloud serverless functions (AWS Lambda). Vercel **cannot** access `localhost` on your personal laptop.
- Therefore, for the cloud deployment to load real books, members, and transactions, you need a **cloud-hosted MySQL database**.

### Free Cloud MySQL Providers:
You can create a free cloud MySQL database in 2 minutes on any of these platforms:
1. **[Aiven for MySQL](https://aiven.io/)** (Free tier available)
2. **[TiDB Cloud Serverless](https://tidbcloud.com/)** (Free tier, fully MySQL 8.0 wire-compatible)
3. **[Railway](https://railway.app/)** (Quick 1-click MySQL provisioning)
4. **[Clever Cloud](https://www.clever-cloud.com/)** (Free MySQL addon)

Once your cloud MySQL database is created:
1. Run [`database/schema.sql`](../database/schema.sql) in your cloud database console / MySQL Workbench.
2. Run [`database/sample_data.sql`](../database/sample_data.sql) to seed the catalogue, patrons, and loans.

*(Note: If no database is connected yet, the application gracefully renders an informative database configuration page rather than throwing a 500 error).*

---

## 2. Deploying via Vercel Dashboard (Recommended — 2 Minutes)

Since your code is already pushed to GitHub at [TeamDDPratham/Library-Management-System](https://github.com/TeamDDPratham/Library-Management-System), deploying via the Vercel Dashboard is the simplest and most reliable method:

1. Go to **[vercel.com](https://vercel.com)** and sign in with your GitHub account.
2. Click **"Add New..."** -> **"Project"**.
3. Under **"Import Git Repository"**, select **`TeamDDPratham/Library-Management-System`** and click **Import**.
4. In the **Configure Project** screen:
   - **Framework Preset**: Other (leave default)
   - **Root Directory**: `./` (leave default)
5. Expand the **"Environment Variables"** section and add the following keys:

| Environment Variable | Value Example | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `your-secure-random-secret-key-12345` | Flask session encryption key |
| `DB_HOST` | `your-db-host.tidbcloud.com` | Cloud MySQL host |
| `DB_PORT` | `3306` (or provider's port, e.g., `4000`) | MySQL port |
| `DB_USER` | `your_db_username` | MySQL username |
| `DB_PASSWORD` | `your_db_password` | MySQL password |
| `DB_NAME` | `LibraryDB` | Database schema name |
| `CURRENCY_SYMBOL` | `₹` | Indian Rupee currency standard |
| `FINE_PER_DAY` | `5.00` | Penalty fine rate per day |

6. Click **Deploy**.
7. Vercel will build the Python environment, install `requirements.txt`, and provide you with a live URL (e.g. `https://library-management-system-xyz.vercel.app`).

---

## 3. Alternative: Deploying via Vercel CLI

If you prefer using the command line:

1. Open PowerShell in the project directory:
   ```powershell
   cd "c:\Users\Pratam Jain\Desktop\Library Management System"
   ```
2. Log in to Vercel:
   ```powershell
   npx vercel login
   ```
   *(This will open your browser to authorize your Vercel account).*
3. Deploy to preview:
   ```powershell
   npx vercel
   ```
4. Deploy to production:
   ```powershell
   npx vercel --prod
   ```

---

## 4. How the Vercel Configuration Works

- **[`api/index.py`](../api/index.py)**: Acts as the serverless WSGI entrypoint that loads your Flask `app`.
- **[`vercel.json`](../vercel.json)**: Directs all web traffic (`/(.*)`) to the serverless function `/api/index`.
- **[`requirements.txt`](../requirements.txt)**: Specifies dependencies (`Flask`, `mysql-connector-python`, `python-dotenv`) that Vercel installs automatically.
