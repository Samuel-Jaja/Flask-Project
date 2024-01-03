from flask import Flask, redirect, request, render_template, url_for
import numpy as np
from scipy.optimize import fsolve

app = Flask(__name__)

# Antoine equation parameters for components
antoine_parameters = {
    'ethane': {'A': 8.14019, 'B': 1810.94, 'C': 244.485},
    'propane': {'A': 7.50024, 'B': 1554.679, 'C': 222.65},
    'butane': {'A': 8.07131, 'B': 1730.63, 'C': 233.426},
    'pentane': {'A': 7.73148, 'B': 1656.793, 'C': 228.5},
    'others': {'A': 7.5, 'B': 1500, 'C': 200}
}

# Function to calculate vapor pressure using Antoine equation
def calculate_vapor_pressure(A, B, C, temperature):
    return 10 ** (A - (B / (temperature + C)))

# Function to calculate saturation temperature for a component
def calculate_saturation_temperature(A, B, C, pressure):
    return B / (A - np.log10(pressure)) - C

# Function to calculate bubble point temperature for binary mixtures
def bubble_point_temperature_binary(antoine_parameters, pressure, x1, x2):
    selected_components = request.form.getlist('selected_components')

    # Extract Antoine parameters for the selected components
    A_values, B_values, C_values = zip(
        *(antoine_parameters[component].values() for component in selected_components)
    )

    # Calculate the saturation temperatures for each selected component
    Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]

    # Calculate the initial guess for the mixture temperature
    Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2], Tsat_values))

    # Define the equation to solve for binary mixture
    def to_solve(T):
        P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
        return sum(P * xi for P, xi in zip(P_values, [x1, x2])) - pressure

    # Use the initial guess in the fsolve function
    return fsolve(to_solve, Tguess)[0]

# Function to calculate bubble point temperature for ternary mixtures
def bubble_point_temperature_ternary(antoine_parameters, pressure, x1, x2, x3):
    selected_components = request.form.getlist('selected_components')

    # Extract Antoine parameters for the selected components
    A_values, B_values, C_values = zip(
        *(antoine_parameters[component].values() for component in selected_components)
    )

    # Calculate the saturation temperatures for each selected component
    Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]

    # Calculate the initial guess for the mixture temperature
    Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2, x3], Tsat_values))

    # Define the equation to solve for ternary mixture
    def to_solve(T):
        P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
        return sum(P * xi for P, xi in zip(P_values, [x1, x2, x3])) - pressure

    # Use the initial guess in the fsolve function
    return fsolve(to_solve, Tguess)[0]

# Function to calculate dew point temperature for binary mixtures
def dew_point_temperature_binary(antoine_parameters, pressure, x1, x2):
    selected_components = request.form.getlist('selected_components')

    # Extract Antoine parameters for the selected components
    A_values, B_values, C_values = zip(
        *(antoine_parameters[component].values() for component in selected_components)
    )

    # Calculate the initial guess for the mixture temperature
    Tguess = 300  # Initial guess for dew point temperature

    # Define the equation to solve for binary mixture dew point
    def to_solve(T):
        P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
        return sum(P * xi for P, xi in zip(P_values, [x1, x2])) - pressure

    # Use the initial guess in the fsolve function
    return fsolve(to_solve, Tguess)[0]

# Function to calculate dew point temperature for ternary mixtures
def dew_point_temperature_ternary(antoine_parameters, pressure, x1, x2, x3):
    selected_components = request.form.getlist('selected_components')

    # Extract Antoine parameters for the selected components
    A_values, B_values, C_values = zip(
        *(antoine_parameters[component].values() for component in selected_components)
    )

    # Calculate the initial guess for the mixture temperature
    Tguess = 300  # Initial guess for dew point temperature

    # Define the equation to solve for ternary mixture dew point
    def to_solve(T):
        P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
        return sum(P * xi for P, xi in zip(P_values, [x1, x2, x3])) - pressure

    # Use the initial guess in the fsolve function
    return fsolve(to_solve, Tguess)[0]

# Route for bubble point computation
@app.route('/bubble_point_computation', methods=['GET', 'POST'])
def bubble_point_computation():
    if request.method == 'POST':
        pressure_str = request.form['pressure']
        mixture_type = request.form['mixture_type']
        selected_components = request.form.getlist('selected_components')

        # Check if pressure is a non-empty string and can be converted to float
        if pressure_str and pressure_str.replace('.', '', 1).isdigit():
            pressure = float(pressure_str)
        else:
            return render_template('error.html', message='Invalid pressure value')

        # Check if the selected components list is not empty
        if not selected_components:
            return render_template('error.html', message='Please select at least one component')

        # Check if the selected components are in the antoine_parameters dictionary
        for component in selected_components:
            if component not in antoine_parameters:
                return render_template('error.html', message=f'Invalid component selected: {component}')

        # Dynamic fraction count based on mixture type
        fractions_count = 2 if mixture_type == 'binary' else 3
        fractions = []

        # Extract mole fractions from the form
        for i in range(1, fractions_count + 1):
            fraction_str = request.form.get(f'x{i}', '')

            # Check if fraction is a non-empty string and can be converted to float
            if fraction_str and fraction_str.replace('.', '', 1).isdigit():
                fractions.append(float(fraction_str))
            else:
                return render_template('error.html', message=f'Invalid mole fraction value for component {i}')

        # Ensure the correct number of fractions is provided
        if len(fractions) != fractions_count:
            return render_template('error.html', message='Invalid number of mole fractions provided')

        # Perform the bubble point computation based on the mixture type
        if mixture_type == 'binary':
            bubble_point = bubble_point_temperature_binary(antoine_parameters, pressure, *fractions)
            print(f"Dew Point: {bubble_point}")
            
 
        elif mixture_type == 'ternary':
            bubble_point = bubble_point_temperature_ternary(antoine_parameters, pressure, *fractions)

        return render_template('result.html', bubble_point=bubble_point, antoine_parameters=antoine_parameters)

    # Pass antoine_parameters to the template for dynamic component selection
    return render_template('bubble_point_computation.html', antoine_parameters=antoine_parameters)

#Flask route for dew point computation
@app.route('/dew_point_computation', methods=['GET', 'POST'])
def dew_point_computation():
    if request.method == 'POST':
        pressure_str = request.form['pressure']
        mixture_type = request.form['mixture_type']
        selected_components = request.form.getlist('selected_components')

        # Check if pressure is a non-empty string and can be converted to float
        if pressure_str and pressure_str.replace('.', '', 1).isdigit():
            pressure = float(pressure_str)
        else:
            return render_template('error.html', message='Invalid pressure value')

        # Check if the selected components list is not empty
        if not selected_components:
            return render_template('error.html', message='Please select at least one component')

        # Check if the selected components are in the antoine_parameters dictionary
        for component in selected_components:
            if component not in antoine_parameters:
                return render_template('error.html', message=f'Invalid component selected: {component}')

        # Dynamic fraction count based on mixture type
        fractions_count = 2 if mixture_type == 'binary' else 3
        fractions = []

        # Extract mole fractions from the form
        for i in range(1, fractions_count + 1):
            fraction_str = request.form.get(f'x{i}', '')

            # Check if fraction is a non-empty string and can be converted to float
            if fraction_str and fraction_str.replace('.', '', 1).isdigit():
                fractions.append(float(fraction_str))
            else:
                return render_template('error.html', message=f'Invalid mole fraction value for component {i}')

        # Ensure the correct number of fractions is provided
        if len(fractions) != fractions_count:
            return render_template('error.html', message='Invalid number of mole fractions provided')

        # Perform the dew point computation based on the mixture type
        if mixture_type == 'binary':
            dew_point = dew_point_temperature_binary(antoine_parameters, pressure, *fractions)
            print(f"Dew Point: {dew_point}")

        elif mixture_type == 'ternary':
            dew_point = dew_point_temperature_ternary(antoine_parameters, pressure, *fractions)
            print(f"Dew Point: {dew_point}")

        #rounded Answer
        rounded_dew_point = round(dew_point)    


        #return render_template('dewpointresult.html', temperature=dew_point, calculation_type='Dew Point')
        return render_template('dewpointresult.html', dew_point=rounded_dew_point, antoine_parameters=antoine_parameters)

    # Pass antoine_parameters to the template for dynamic component selection
    return render_template('dew_point_computation.html', antoine_parameters=antoine_parameters)


@app.route('/')
def landing_page():
    return render_template('landing_page.html')


# @app.route('/dew_point_computation')
# def dew_point_computation():
#     return render_template('dew_point_computation.html')

@app.route('/developer')
def developer_page():
    return render_template('developer.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        # Extract signup form data and call the signup function from your JavaScript
        return redirect(url_for('login'))

    # Render the signup page
    return render_template('signup.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract login form data and call the login function from your JavaScript
        # return render_template('signin.html')
        return redirect(url_for('landing_page'))

    # Render the login page
    return render_template('signin.html')    

if __name__ == '__main__':
    app.run(debug=True)
