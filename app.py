
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
app.secret_key = 'student_project_secret_key_2025'

# error handling
def get_db_connection():
    """
    Establishes connection to the SQLite database.
    Uses try/except to handle missing database file.
    """
    try:
        conn = sqlite3.connect('immunisation.db')
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# HOME PAGE 

@app.route('/')
def index():
    """
    Home page showing project overview and navigation to all A-Level and B-Level pages.
    """
    return render_template('index.html')

# A-LEVEL 1 - Landing Page with Key Vaccination Insights

@app.route('/a_level1')
def a_level1():
    """
    A-Level 1: Landing page displaying 4 key vaccination insights from database.
    """
    conn = get_db_connection()
    
    # Initialise variabls
    year_range = None
    total_vaccinations = None
    disease_count = None
    diseases = []
    error_message = None
    
    if conn:
        try:
            # Query 1: Get year range from Vaccination table
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MIN(year) as min_year, MAX(year) as max_year 
                FROM Vaccination
            """)
            year_data = cursor.fetchone()
            year_range = f"{year_data['min_year']} to {year_data['max_year']}"
            
            # Query 2: Count total vaccination records
            cursor.execute("SELECT COUNT(*) as count FROM Vaccination")
            total_vaccinations = cursor.fetchone()['count']
            
            # Query 3: Count distinct infectious diseases
            cursor.execute("SELECT COUNT(*) as count FROM Infection_Type")
            disease_count = cursor.fetchone()['count']
            
            # Query 4: Get list of all infectious diseases
            cursor.execute("SELECT description FROM Infection_Type ORDER BY description")
            diseases = cursor.fetchall()
            
        except sqlite3.Error as e:
            error_message = f"Database query error: {e}"
        finally:
            conn.close()
    else:
        error_message = "Unable to connect to database. Please ensure immunisation.db exists."
    
    return render_template('a_level1.html', 
                         year_range=year_range,
                         total_vaccinations=total_vaccinations,
                         disease_count=disease_count,
                         diseases=diseases,
                         error_message=error_message)


# A-LEVEL 2

@app.route('/a_level2', methods=['GET', 'POST'])
def a_level2():
    """
    A-Level 2: Interactive page showing vaccination coverage analysis.
    Allows filtering by Year and Antigen type.
    
    Displays two tables:
    - Table 1: Countries with >= 90% coverage for selected antigen/year
    - Table 2: Count of countries meeting 90% target per region

    """
    conn = get_db_connection()
    
    # Variables for  dropdowns and result
    years = []
    antigens = []
    countries_table = []
    regions_table = []
    error_message = None
    selected_year = None
    selected_antigen = None
    
    if conn:
        try:
            # Get available years for dropdown 
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT year FROM Vaccination ORDER BY year DESC")
            years = [row['year'] for row in cursor.fetchall()]
            
            # Get available antigens for dropdown
            cursor.execute("SELECT DISTINCT antigen FROM Vaccination ORDER BY antigen")
            antigens = [row['antigen'] for row in cursor.fetchall()]
            
            # If form submitted with POST request
            if request.method == 'POST':
                selected_year = request.form.get('year')
                selected_antigen = request.form.get('antigen')
                
                if selected_year and selected_antigen:
                    # Table 1: Countries with >= 90% coverage
                    # JOIN Vaccination, Country, and Region tables
                    cursor.execute("""
                        SELECT 
                            v.antigen,
                            v.year,
                            c.name as country_name,
                            r.region,
                            v.coverage
                        FROM Vaccination v
                        INNER JOIN Country c ON v.country = c.CountryID
                        INNER JOIN Region r ON c.region = r.RegionID
                        WHERE v.year = ? AND v.antigen = ? AND v.coverage >= 90
                        ORDER BY v.coverage DESC, c.name
                    """, (selected_year, selected_antigen))
                    countries_table = cursor.fetchall()
                    
                    # Table 2: Count of countries meeting 90% target per region
                    # Uses GROUP BY to aggregate by region
                    cursor.execute("""
                        SELECT 
                            v.antigen,
                            v.year,
                            r.region,
                            COUNT(DISTINCT c.CountryID) as country_count
                        FROM Vaccination v
                        INNER JOIN Country c ON v.country = c.CountryID
                        INNER JOIN Region r ON c.region = r.RegionID
                        WHERE v.year = ? AND v.antigen = ? AND v.coverage >= 90
                        GROUP BY r.region
                        ORDER BY country_count DESC, r.region
                    """, (selected_year, selected_antigen))
                    regions_table = cursor.fetchall()
                    
        except sqlite3.Error as e:
            error_message = f"Database query error: {e}"
        finally:
            conn.close()
    else:
        error_message = "Unable to connect to database."
    
    return render_template('a_level2.html',
                         years=years,
                         antigens=antigens,
                         countries_table=countries_table,
                         regions_table=regions_table,
                         selected_year=selected_year,
                         selected_antigen=selected_antigen,
                         error_message=error_message)


# A-LEVEL 3 

@app.route('/a_level3', methods=['GET', 'POST'])
def a_level3():
    """
    A-Level 3: Analysis of vaccination rate improvements.
    Allows user to select:
    - Start year and end year
    - Antigen type
    - Number of top countries to display
    
    Calculates vaccination rate improvement between two years.
    Uses JOINs across Vaccination and CountryPopulation tables.
    """
    conn = get_db_connection()
    
    years = []
    antigens = []
    results = []
    error_message = None
    start_year = None
    end_year = None
    selected_antigen = None
    top_n = 10  # Default value
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get available years and antigens for dropdowns
            cursor.execute("SELECT DISTINCT year FROM Vaccination ORDER BY year")
            years = [row['year'] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT antigen FROM Vaccination ORDER BY antigen")
            antigens = [row['antigen'] for row in cursor.fetchall()]
            
            # If form submitted
            if request.method == 'POST':
                start_year = request.form.get('start_year')
                end_year = request.form.get('end_year')
                selected_antigen = request.form.get('antigen')
                top_n = int(request.form.get('top_n', 10))
                
                if start_year and end_year and selected_antigen:
                    # Calculate vaccination rate improvement
                    # Rate = (coverage * population) / population for consistency
                    # Improvement = end_coverage - start_coverage
                    cursor.execute("""
                        SELECT 
                            c.name as country_name,
                            (v2.coverage - v1.coverage) as rate_increase,
                            v1.coverage as start_coverage,
                            v2.coverage as end_coverage,
                            ? as start_year,
                            ? as end_year
                        FROM Vaccination v1
                        INNER JOIN Vaccination v2 
                            ON v1.country = v2.country 
                            AND v1.antigen = v2.antigen
                        INNER JOIN Country c ON v1.country = c.CountryID
                        WHERE v1.year = ? 
                            AND v2.year = ?
                            AND v1.antigen = ?
                            AND v2.coverage > v1.coverage
                        ORDER BY rate_increase DESC
                        LIMIT ?
                    """, (start_year, end_year, start_year, end_year, selected_antigen, top_n))
                    results = cursor.fetchall()
                    
        except sqlite3.Error as e:
            error_message = f"Database query error: {e}"
        finally:
            conn.close()
    else:
        error_message = "Unable to connect to database."
    
    return render_template('a_level3.html',
                         years=years,
                         antigens=antigens,
                         results=results,
                         start_year=start_year,
                         end_year=end_year,
                         selected_antigen=selected_antigen,
                         top_n=top_n,
                         error_message=error_message)


# B-LEVEL 1 - Mission Statement

@app.route('/b_level1')
def b_level1():
    """
    B-Level 1: Mission statement page showing:
    - Project purpose and how it addresses the social challenge
    - Target personas 
    - Team member names and student numbers (static data)
    """
    conn = get_db_connection()
    
    personas = []
    error_message = None

    # Static team member list
    team_members = [
        {'name': 'Mohamad Otman', 'student_id': 's4091213'},
        {'name': 'Ahnab', 'student_id': 's4200011'}
    ]
    
    if conn:
        try:
            cursor = conn.cursor()

            # Try to fetch personas from DB; fallback to static examples if table missing
            try:
                cursor.execute("SELECT * FROM Persona LIMIT 5")
                personas = cursor.fetchall()
            except sqlite3.Error:
                personas = [
                    {'name': 'Health Policy Maker', 'description': 'Government officials analyzing vaccination program effectiveness'},
                    {'name': 'Medical Researcher', 'description': 'Scientists studying disease prevention patterns'},
                    {'name': 'Public Health Educator', 'description': 'Educators seeking data to inform communities'}
                ]
                
        except sqlite3.Error as e:
            error_message = f"Database query error: {e}"
        finally:
            conn.close()
    else:
        error_message = "Unable to connect to database."
    
    return render_template(
        'b_level1.html',
        personas=personas,
        team_members=team_members,
        error_message=error_message
    )


# B-LEVEL 2 - Infection Data by Economic Status

@app.route('/b_level2', methods=['GET', 'POST'])
def b_level2():
    """
    B-Level 2: Focused view of infection data filtered by economic status.
    Allows filtering by:
    - Economic status (Economy.phase)
    - Infection type
    - Year
    """
    conn = get_db_connection()
    
    economic_statuses = []
    infection_types = []
    years = []
    detailed_results = []
    summary_results = []
    error_message = None
    selected_economy = None
    selected_infection = None
    selected_year = None
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get available economic statuses
            cursor.execute("SELECT DISTINCT phase FROM Economy ORDER BY phase")
            economic_statuses = [row['phase'] for row in cursor.fetchall()]
            
            # Get available infection types
            cursor.execute("SELECT id, description FROM Infection_Type ORDER BY description")
            infection_types = cursor.fetchall()
            
            # Get available years from InfectionData
            cursor.execute("SELECT DISTINCT year FROM InfectionData ORDER BY year DESC")
            years = [row['year'] for row in cursor.fetchall()]
            
            # If form submitted
            if request.method == 'POST':
                selected_economy = request.form.get('economy')
                selected_infection = request.form.get('infection_type')
                selected_year = request.form.get('year')
                
                if selected_economy and selected_infection and selected_year:
                    # Detailed table: Cases per 100,000 people
                    # Calculate: (cases / population) * 100,000
                    cursor.execute("""
                        SELECT 
                            it.description as disease,
                            c.name as country,
                            e.phase as economic_phase,
                            id.year,
                            ROUND((id.cases * 100000.0 / cp.population), 2) as cases_per_100k,
                            id.cases as total_cases
                        FROM InfectionData id
                        INNER JOIN Country c ON id.country = c.CountryID
                        INNER JOIN Economy e ON c.economy = e.economyID
                        INNER JOIN Infection_Type it ON id.inf_type = it.id
                        INNER JOIN CountryPopulation cp 
                            ON id.country = cp.country AND id.year = cp.year
                        WHERE e.phase = ? 
                            AND it.id = ?
                            AND id.year = ?
                        ORDER BY cases_per_100k DESC
                    """, (selected_economy, selected_infection, selected_year))
                    detailed_results = cursor.fetchall()
                    
                    # Summary table: Total cases by economic phase
                    # Uses GROUP BY to aggregate data
                    cursor.execute("""
                        SELECT 
                            it.description as disease,
                            e.phase as economic_phase,
                            id.year,
                            SUM(id.cases) as total_cases,
                            COUNT(DISTINCT c.CountryID) as country_count
                        FROM InfectionData id
                        INNER JOIN Country c ON id.country = c.CountryID
                        INNER JOIN Economy e ON c.economy = e.economyID
                        INNER JOIN Infection_Type it ON id.inf_type = it.id
                        WHERE it.id = ? AND id.year = ?
                        GROUP BY e.phase
                        ORDER BY total_cases DESC
                    """, (selected_infection, selected_year))
                    summary_results = cursor.fetchall()
                    
        except sqlite3.Error as e:
            error_message = f"Database query error: {e}"
        finally:
            conn.close()
    else:
        error_message = "Unable to connect to database."
    
    return render_template('b_level2.html',
                         economic_statuses=economic_statuses,
                         infection_types=infection_types,
                         years=years,
                         detailed_results=detailed_results,
                         summary_results=summary_results,
                         selected_economy=selected_economy,
                         selected_infection=selected_infection,
                         selected_year=selected_year,
                         error_message=error_message)


# B-LEVEL 3 - Countries with Above Average Infection Rate

@app.route('/b_level3', methods=['GET', 'POST'])
def b_level3():
    """
    B-Level 3: Deep analysis showing countries with above-average infection rates.
    User selects:
    - Infection type
    - Year
    - Number of top countries to display
    """
    conn = get_db_connection()
    
    infection_types = []
    years = []
    results = []
    global_average = None
    error_message = None
    selected_infection = None
    selected_year = None
    top_n = 10  # Default
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get available infection types
            cursor.execute("SELECT id, description FROM Infection_Type ORDER BY description")
            infection_types = cursor.fetchall()
            
            # Get available years
            cursor.execute("SELECT DISTINCT year FROM InfectionData ORDER BY year DESC")
            years = [row['year'] for row in cursor.fetchall()]
            
            # If form submitted
            if request.method == 'POST':
                selected_infection = request.form.get('infection_type')
                selected_year = request.form.get('year')
                top_n = int(request.form.get('top_n', 10))
                
                if selected_infection and selected_year:
                    # Calculate global average infection rate per 100,000
                    cursor.execute("""
                        SELECT 
                            AVG((id.cases * 100000.0 / cp.population)) as avg_rate
                        FROM InfectionData id
                        INNER JOIN CountryPopulation cp 
                            ON id.country = cp.country AND id.year = cp.year
                        WHERE id.inf_type = ? AND id.year = ?
                    """, (selected_infection, selected_year))
                    avg_result = cursor.fetchone()
                    global_average = round(avg_result['avg_rate'], 2) if avg_result['avg_rate'] else 0
                    
                    # Get countries with above-average infection rates
                    
                    cursor.execute("""
                        SELECT 
                            c.name as country,
                            it.description as infection_type,
                            ROUND((id.cases * 100000.0 / cp.population), 2) as infection_per_100k,
                            id.year,
                            id.cases as total_cases
                        FROM InfectionData id
                        INNER JOIN Country c ON id.country = c.CountryID
                        INNER JOIN Infection_Type it ON id.inf_type = it.id
                        INNER JOIN CountryPopulation cp 
                            ON id.country = cp.country AND id.year = cp.year
                        WHERE id.inf_type = ? 
                            AND id.year = ?
                            AND (id.cases * 100000.0 / cp.population) > (
                                SELECT AVG((cases * 100000.0 / population))
                                FROM InfectionData id2
                                INNER JOIN CountryPopulation cp2 
                                    ON id2.country = cp2.country AND id2.year = cp2.year
                                WHERE id2.inf_type = ? AND id2.year = ?
                            )
                        ORDER BY infection_per_100k DESC
                        LIMIT ?
                    """, (selected_infection, selected_year, selected_infection, selected_year, top_n))
                    results = cursor.fetchall()
                    
        except sqlite3.Error as e:
            error_message = f"Database query error: {e}"
        finally:
            conn.close()
    else:
        error_message = "Unable to connect to database."
    
    return render_template('b_level3.html',
                         infection_types=infection_types,
                         years=years,
                         results=results,
                         global_average=global_average,
                         selected_infection=selected_infection,
                         selected_year=selected_year,
                         top_n=top_n,
                         error_message=error_message)


# Application Entry Point
if __name__ == '__main__':
    # Run Flask development server (localhost)
    app.run(host='127.0.0.1', port=5000, debug=True)


if __name__ == "__main__":
    app.run(debug=True)
