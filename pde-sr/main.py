from Population import Population
# %pip install pysr
import numpy as np
import scipy.io as scio

# map u(x,t), given field (burgers eq), Where the function will be x,t,u
data = scio.loadmat('./data/burgers.mat')
u=data.get("usol").T

# we want to find du/dt, aka a partial differential equation described a change over time for field u(x,t)
# du/dt  is also given field
x=np.squeeze(data.get("x"))
t=np.squeeze(data.get("t").reshape(1,201))

# first gradient with respect
# u_x = np.apply_along_axis(np.gradient, 0, u, 0.625, edge_order=2)
u_x = np.apply_along_axis(np.gradient, 1, u, x)
u_t = np.apply_along_axis(np.gradient, 0, u, t)

# # second gradient
u_xx = np.apply_along_axis(np.gradient, 1, u_x, x)
u_tt = np.apply_along_axis(np.gradient, 0, u_t, t)

uu_x = u * u_x

def FiniteDiff(u, dx):

    n = u.size
    ux = np.zeros(n)

    for i in range(1, n - 1):
        ux[i] = (u[i + 1] - u[i - 1]) / (2 * dx)

    ux[0] = (-3.0 / 2 * u[0] + 2 * u[1] - u[2] / 2) / dx
    ux[n - 1] = (3.0 / 2 * u[n - 1] - 2 * u[n - 2] + u[n - 3] / 2) / dx
    return ux
# print(x.shape)
# print(u_x.shape)
# print(u_x[0].shape)
# print(u_x[0])
# print(FiniteDiff(u[:,0], x[2] - x[1]))
# print(u_x[1] == FiniteDiff(u[1,:], x[2] - x[1]))
u_t_solved = 0.1*u_xx - uu_x
mse = ((u_t - u_t_solved)**2).mean(axis=-1).mean()
print(f"Initial error in data: {mse}")
# print(u_t==u_t_solved)
# print(u.shape)

def first_gradient(u, x=x):
    return np.apply_along_axis(np.gradient, 1, u, x)
def second_gradient(u, x=x):
    return np.apply_along_axis(np.gradient, 1, np.apply_along_axis(np.gradient, 1, u, x), x)
def nonlinear_part(u, x=x):
    return u*np.apply_along_axis(np.gradient, 1, u, x)
def add(left, right):
    return left + right
def multiply(left,right):
    return left*right
def subtract(left, right):
    return left-right


# Test if error is the same using functions
u_t_solved_functions = 0.1* second_gradient(u) - u * first_gradient(u)
mse = ((u_t - u_t_solved_functions)**2).mean(axis=-1).mean()
print(f"Error from functions: {mse}")

# Test MSE for wrong functions
non_sensical = u * first_gradient(u)
mse_non_sensical = mse = ((u_t - non_sensical)**2).mean(axis=-1).mean()
print(f"Error between u_t and nonlinear part: {mse_non_sensical}")

# Test MSE wrong functions
non_sensical = 0.1 * second_gradient(u)
mse_non_sensical = mse = ((u_t - non_sensical)**2).mean(axis=-1).mean()
print(f"Error between u_t and second gradient part: {mse_non_sensical}")


operators = {'+': 2,
         '-':2,
         '*':2,
         'first_grad':1,
         'second_grad':1}

terminals = [("u", u, "matrix"),
             ("1", 1, "scalar")]

population = Population(n_trees=50, operators=operators, terminals=terminals, desired_value=u_t)
# mutate tree test
for i in population.trees:
    # print(f"dflksjdf: {i.root.children[0].parent}")
    i.mutate()