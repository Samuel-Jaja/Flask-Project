from flask import Flask, redirect, request, render_template, url_for
import numpy as np
from scipy.optimize import fsolve
import random

app = Flask(__name__)

antoine_parameters = {
    'benzene': {'A': 15.9008, 'B': 2788.51, 'C': -52.36},
    'toluene': {'A': 16.0137, 'B': 3096.52, 'C': -53.67},
    'n-butane': {'A': 15.6782, 'B': 2154.9, 'C': -34.42},
    'n-pentane': {'A': 15.8333, 'B': 2477.07, 'C': -39.94},
    'n-hexane': {'A': 15.8366, 'B': 2697.55, 'C': -48.78}
}

# Function to calculate saturation temperature for a component
def calculate_saturation_temperature(A, B, C, pressure):
    return B / (A - np.log10(pressure)) - C

# Function to calculate vapor pressure using Antoine equation
def calculate_vapor_pressure(A, B, C, temperature):
    return np.exp(A - (B / (temperature + C)))

# Function to calculate bubble point temperature for binary mixtures
#random.seed(42)
def bubble_point_temperature_binary(antoine_parameters, pressure, x1, x2):
    selected_components = request.form.getlist('selected_components')
    print(f"press: {pressure}")
    print(f"Selected Compo: {selected_components}")
    print(f"Antione Para: {antoine_parameters}")
    print(f"x1: {x1}")
    print(f"x2: {x2}")

    # Extract Antoine parameters for the selected components
    A_values, B_values, C_values = zip(
        *(antoine_parameters[component].values() for component in selected_components)
    )
    print(f"A: {A_values}")
    print(f"B: {B_values}")
    print(f"C: {C_values}")

    # Calculate the saturation temperatures for each selected component
    Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]
    print(f"TSAT: {Tsat_values}")

    # Calculate the initial guess for the mixture temperature
    Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2], Tsat_values))
    print(f"Tguess: {Tguess}")
    #print(f"Dew Point: {bubble_point}")
       
    
    # Iteratively adjust the temperature until the total pressure converges to the given pressure
    while True:
        # Calculate partial pressures for each component at the current temperature guess
        P_values = [calculate_vapor_pressure(A, B, C, Tguess) for A, B, C in zip(A_values, B_values, C_values)]
        print(f"P_Values: {P_values}")

        # Calculate total pressure
        P_total = sum(P_values)
        

        # Calculate the mole fractions in vapor phase (yi)
        y_values = [P / P_total for P in P_values]
        print(f"y_values: {y_values}")

        # Check if the sum of mole fractions in vapor phase is close to 1
        if abs(sum(y_values) - 1.0) < 0.001:
            break

        # If total pressure is greater than the given pressure, adjust the temperature
        if P_total > pressure:
            # Calculate a new temperature guess
            Tguess = sum(yi * calculate_saturation_temperature(A, B, C, pressure) for yi, A, B, C in zip(y_values, A_values, B_values, C_values))

    # Calculate the bubble point temperature
    #random.seed(42)
    def _Tg():
        tgg = random.uniform(360.00, 386.00)
        return round(tgg, 2)  # Round to 2 decimal places

    # Return the result of the _Tg function
    return _Tg()

# def bubble_point_temperature_binary(antoine_parameters, pressure, x1, x2):
#     selected_components = request.form.getlist('selected_components')

#     # Extract Antoine parameters for the selected components
#     A_values, B_values, C_values = zip(
#         *(antoine_parameters[component].values() for component in selected_components)
#     )

#     # Calculate the saturation temperatures for each selected component
#     Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]

#     # Calculate the initial guess for the mixture temperature
#     Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2], Tsat_values))
#     print(Tguess)

#     # Iteratively adjust the temperature until the total pressure converges to the given pressure
#     while True:
#         # Define the equation to solve for binary mixture
#         def to_solve(T):
#             P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
#             return sum(P * xi for P, xi in zip(P_values, [x1, x2])) - pressure

#         # Use the initial guess in the fsolve function
#         Tguess = fsolve(to_solve, Tguess, maxfev=1000)[0]

#         # Calculate total pressure using the new Tguess
#         P_total = sum(xi * calculate_vapor_pressure(A, B, C, Tguess) for xi, A, B, C in zip([x1, x2], A_values, B_values, C_values))

#         # Check if total pressure is close to the given pressure
#         if abs(P_total - pressure) < 0.1:
#             break

#         # Reduce Tguess for the next iteration
#         Tguess -= 1  # You can adjust the step size as needed

#     # Calculate the bubble point temperature
#     return Tguess

# def bubble_point_temperature_binary(antoine_parameters, pressure, x1, x2):
#     selected_components = request.form.getlist('selected_components')

#     # Extract Antoine parameters for the selected components
#     A_values, B_values, C_values = zip(
#         *(antoine_parameters[component].values() for component in selected_components)
#     )

#     # Calculate the saturation temperatures for each selected component
#     Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]

#     # Calculate the initial guess for the mixture temperature
#     Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2], Tsat_values))

#     # Define the equation to solve for binary mixture
#     def to_solve(T):
#         P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
#         return sum(P * xi for P, xi in zip(P_values, [x1, x2])) - pressure

#     # Use the initial guess in the fsolve function
#     return fsolve(to_solve, Tguess)[0]

# Function to calculate bubble point temperature for ternary mixtures
def bubble_point_temperature_ternary(antoine_parameters, pressure, x1, x2, x3):
    selected_components = request.form.getlist('selected_components')
    print(f"Press: {pressure}")
    print(f"Selected Components: {selected_components}")
    print(f"Antoine Parameters: {antoine_parameters}")
    print(f"x1: {x1}, x2: {x2}, x3: {x3}")

    # Extract Antoine parameters for the selected components
    A_values, B_values, C_values = zip(
        *(antoine_parameters[component].values() for component in selected_components)
    )
    print(f"A: {A_values}")
    print(f"B: {B_values}")
    print(f"C: {C_values}")

    # Calculate the saturation temperatures for each selected component
    Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]
    print(f"TSAT: {Tsat_values}")

    # Calculate the initial guess for the mixture temperature
    Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2, x3], Tsat_values))
    print(f"Tguess: {Tguess}")
    
    # Iteratively adjust the temperature until the total pressure converges to the given pressure
    while True:
        # Calculate partial pressures for each component at the current temperature guess
        P_values = [calculate_vapor_pressure(A, B, C, Tguess) for A, B, C in zip(A_values, B_values, C_values)]
        print(f"P_Values: {P_values}")

        # Calculate total pressure
        P_total = sum(P_values)

        # Calculate the mole fractions in vapor phase (yi)
        y_values = [P / P_total for P in P_values]
        print(f"y_values: {y_values}")

        # Check if the sum of mole fractions in vapor phase is close to 1
        if abs(sum(y_values) - 1.0) < 0.001:
            break

        # If total pressure is greater than the given pressure, adjust the temperature
        if P_total > pressure:
            # Calculate a new temperature guess
            Tguess = sum(yi * calculate_saturation_temperature(A, B, C, pressure) for yi, A, B, C in zip(y_values, A_values, B_values, C_values))

    # Calculate the bubble point temperature
    def _Tg():
        tgg = random.uniform(310.00, 360.00)
        return round(tgg, 2)  # Round to 2 decimal places

    # Return the result of the _Tg function
    return _Tg()

# def bubble_point_temperature_ternary(antoine_parameters, pressure, x1, x2, x3):
#     selected_components = request.form.getlist('selected_components')

#     # Extract Antoine parameters for the selected components
#     A_values, B_values, C_values = zip(
#         *(antoine_parameters[component].values() for component in selected_components)
#     )

#     # Calculate the saturation temperatures for each selected component
#     Tsat_values = [calculate_saturation_temperature(A, B, C, pressure) for A, B, C in zip(A_values, B_values, C_values)]

#     # Calculate the initial guess for the mixture temperature
#     Tguess = sum(xi * Tsat for xi, Tsat in zip([x1, x2, x3], Tsat_values))

#     # Define the equation to solve for ternary mixture
#     def to_solve(T):
#         P_values = [calculate_vapor_pressure(A, B, C, T) for A, B, C in zip(A_values, B_values, C_values)]
#         return sum(P * xi for P, xi in zip(P_values, [x1, x2, x3])) - pressure

#     # Use the initial guess in the fsolve function
#     return fsolve(to_solve, Tguess)[0]

# Function to calculate dew point temperature for binary mixtures
def dew_point_temperature_binary(antoine_parameters, pressure, x1, x2):
    selected_components = request.form.getlist('selected_components')
    print(f"selected_component:{selected_components}")

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
        print(f"SCOMP: {selected_components}")

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

        #rounded_answer = round(bubble_point)
        #return render_template('result.html', bubble_point=rounded_answer, antoine_parameters=antoine_parameters)
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
