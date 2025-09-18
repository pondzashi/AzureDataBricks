# Azure Databricks Environment Setup

This repository contains the assets required to stand up a Databricks workspace demo that analyses a small retail dataset. Follow the steps below to prepare your local workstation and Databricks workspace so that the accompanying notebook can be executed without additional manual setup.

## Repository layout

```
.
├── data/                     # CSV source data for the demo notebook
├── notebooks/                # Databricks notebooks (source export format)
└── scripts/                  # Helper scripts for environment bootstrap
```

## 1. Prerequisites

| Tool | Purpose | Notes |
| --- | --- | --- |
| [Python 3.9+](https://www.python.org/downloads/) | Provides a runtime for Databricks CLI and utility scripts | Install via your OS package manager or python.org installer |
| [pip](https://pip.pypa.io/en/stable/installation/) | Installs Python packages into the virtual environment | Included with most Python distributions |
| [Databricks account](https://www.databricks.com/try-databricks) | Workspace in which you will run the notebook | Community Edition works for this project |
| [Databricks personal access token](https://docs.databricks.com/dev-tools/auth/pat.html) | Authenticates CLI actions | Generate within your Databricks workspace |

> **Tip:** On Windows we recommend running the scripts in [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/install) to ensure Unix shell compatibility.

## 2. Create and activate a virtual environment

The repository ships with a helper script that builds a reusable virtual environment under `.venv` and installs the minimal dependencies needed to interact with Databricks.

```bash
bash scripts/setup_env.sh
source .venv/bin/activate
```

You may adjust the virtual environment location by setting the `VENV_DIR` environment variable before invoking the script.

## 3. Configure Databricks CLI credentials

1. Copy the provided template and populate it with your workspace details:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and set `DATABRICKS_HOST` (for example, `https://adb-1234567890123.4.azuredatabricks.net`) and `DATABRICKS_TOKEN`.
3. Run the Databricks CLI configuration command while the virtual environment is active:
   ```bash
   databricks configure --token
   ```
   When prompted, paste the host URL and token values from your `.env` file.

Additional CLI authentication mechanisms (Azure AD, profiles) can also be used—refer to the [Databricks CLI documentation](https://docs.databricks.com/dev-tools/cli/index.html) if you need a different method.

## 4. Upload the sample data to DBFS

After the CLI is configured, push the CSV assets that the notebook consumes into DBFS using the provided helper script. The script syncs files under `data/` to `dbfs:/FileStore/tables/sales_demo/`.

```bash
bash scripts/upload_sample_data.sh
```

You can verify the upload with:

```bash
databricks fs ls dbfs:/FileStore/tables/sales_demo/
```

## 5. Import the demo notebook into your workspace

### Option A – Databricks UI

1. In the Databricks workspace UI, navigate to **Workspace ▸ Users ▸ _your_user_** (or a shared folder of your choice).
2. Click the **Import** button.
3. Select **Source** as the format and upload `notebooks/sales_analytics.py`.

### Option B – Databricks CLI

```bash
databricks workspace import \
  --language PYTHON \
  --format SOURCE \
  notebooks/sales_analytics.py \
  /Users/<your_user>/sales_analytics
```

Update the target path to match your workspace folder hierarchy.

## 6. Run the notebook

1. In Databricks, create (or select) a cluster that uses **Runtime 11.3 LTS (Scala 2.12, Spark 3.3)** or newer.
2. Open the imported `sales_analytics` notebook.
3. Attach the notebook to your cluster and execute the cells sequentially.

The notebook expects the CSV files to exist under `dbfs:/FileStore/tables/sales_demo/`. If you prefer to store them elsewhere, update the `DATASET_ROOT` constant at the top of the notebook accordingly.

## 7. Troubleshooting

- **Module not found errors:** Ensure the cluster has the required libraries installed. The `requirements.txt` file lists the packages used; you can install equivalent library versions on the cluster (via PyPI or init scripts).
- **Authentication issues:** Re-run `databricks configure --token` after rotating your personal access token. Confirm that your `.databrickscfg` file contains the expected profile.
- **Upload script fails:** Verify that the Databricks CLI is available in your `PATH` and that the configured user has DBFS write permissions.

## 8. Next steps

Once everything is working, you can adapt the notebook to your own datasets, add additional notebooks to the `notebooks/` folder, and extend the automation scripts (for example, to create jobs or clusters via the Databricks REST API).
