# Jobbit

Jobbit is a free tool that finds internship and full-time job listings matching your criteria and saves them to a local database. It fills out applications for you using your saved answers and the right resume for each job type, and it stops to ask you whenever it hits a question it hasn't seen before. Finished applications move from **unexplored** to **applied**.

> **Status:** early development. The setup below works today; features are being added step by step (see the roadmap).

## Features

- Finds listings from public job-board APIs (Greenhouse, Lever) using your filters
- Sorts jobs into **internship** and **full-time** categories
- Tracks each job as **unexplored** or **applied**
- Stores your answers to common application questions and reuses them
- Never guesses: if a question has no confident match, it asks you and saves your answer
- Uses a different resume for internships than for full-time roles
- Runs entirely on your computer with free, open-source tools

## Requirements

- **Python 3.10 or newer** (check with `python --version`; on some systems the command is `python3`)
- **Git** (to download the project)
- About 500 MB of free disk space (most of it is the Chromium browser Playwright downloads)

## Installation

### 1. Download the project

```bash
git clone https://github.com/YOUR-USERNAME/jobbit.git
cd jobbit
```

Replace `YOUR-USERNAME` with the account that hosts the repository. If you received the project as a zip file instead, unzip it and open a terminal inside the `jobbit` folder.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

| System | Command |
|---|---|
| Mac / Linux | `source venv/bin/activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| Windows (cmd) | `venv\Scripts\activate.bat` |

You should see `(venv)` at the start of your terminal line.

> **Windows PowerShell error about scripts being disabled?** Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.

### 4. Install Jobbit and its dependencies

```bash
pip install -e .
```

This reads `pyproject.toml` and installs everything Jobbit needs.

### 5. Install the browser used for auto-fill

```bash
playwright install chromium
```

This is a separate step because the browser isn't a pip package.

### 6. Create your local folders

The database and your resumes are kept out of Git because they contain personal information, so create the folders yourself:

```bash
mkdir data resumes
```

Then put your resumes in `resumes/`:

- `resumes/internship.pdf`
- `resumes/full_time.pdf`

### 7. Configure your search

Open `config.yaml` and set your resume paths, keywords, locations, and the companies you want to search:

```yaml
resumes:
  internship: resumes/internship.pdf
  full_time: resumes/full_time.pdf

filters:
  keywords: ["software", "data"]
  exclude: ["senior", "staff", "manager"]
  locations: ["Remote", "New York"]
  remote_ok: true

companies:
  greenhouse: ["stripe", "airbnb"]
  lever: ["palantir"]
```

A company's slug is the last part of its job board URL, for example `boards.greenhouse.io/stripe` uses `stripe`.

### 8. Check that it works

```bash
python -c "import httpx, playwright, streamlit, rapidfuzz, yaml; print('Jobbit is ready')"
```

If you see `Jobbit is ready`, setup is complete.

## Running Jobbit

Every time you open a new terminal, go to the project folder and activate the virtual environment first:

```bash
cd path/to/jobbit
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
```

Then start the dashboard (available once the dashboard step is built):

```bash
streamlit run app.py
```

## Project structure

```
jobbit/
├── app.py              # Streamlit dashboard
├── config.yaml         # your filters, companies, and resume paths
├── pyproject.toml      # project metadata and dependencies
├── data/               # jobbit.db lives here (not tracked by Git)
├── resumes/            # your resumes (not tracked by Git)
└── jobbit/
    ├── db.py           # database tables: jobs, answers, resumes
    └── sources/        # job-board fetchers (Greenhouse, Lever)
```

## Roadmap

1. [x] Project setup
2. [ ] Database (`jobbit.db`)
3. [ ] Config loading
4. [ ] Fetch jobs from Greenhouse into **unexplored**
5. [ ] Dashboard to review jobs and mark them **applied**
6. [ ] Saved answers with ask-and-save flow
7. [ ] Auto-fill with Playwright using the right resume per category

## Notes

- Jobbit does not scrape LinkedIn or Indeed, since that violates their terms of service. It uses public job-board APIs instead.
- Auto-fill starts semi-automatic: it fills the form and you review before submitting.
- Your answers, resumes, and database stay on your computer.

## Troubleshooting

- **`python` not found:** try `python3`, or install Python from python.org.
- **`pip install -e .` fails:** make sure the virtual environment is active and you are in the folder that contains `pyproject.toml`.
- **Playwright browser errors:** re-run `playwright install chromium`.

## License

MIT. Add a `LICENSE` file to the repository root before publishing.