import numpy as np
from scipy.stats import ortho_group
from scipy.stats import unitary_group

import interferometer as itf
import cmath
import math

# Importar el detector automático de Lumerical
import sys
import os
# Añadir el directorio padre al path para poder importar lumerical_path_detector
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lumerical_path_detector import auto_detect_and_load_lumapi

# Cargar lumapi automáticamente
lumapi = auto_detect_and_load_lumapi()

#### some more function definitions

def phase_shifter(name,angle,unidirectional=True,xpos=0,ypos=0):
    """
    Generates and defines a phase shifter with a given name and a given angle

    """

    ic.addelement("Optical Phase Shift Unidirectional")
    if unidirectional==False: 
        ic.set("configuration","bidirectional")
    ic.set("name",name)
    ic.set("phase shift", angle)
    ic.set("x position",0+xpos)
    ic.set("y position",0+ypos)

def dir_coupler(name,coupling_coefficient=0.5,unidirectional=True,conjugate=False,xpos=0,ypos=0):
    """
    Generates and defines a directional coupler with a given name and a given coupling coefficient

    """

    ic.addelement("Waveguide Coupler Unidirectional")
    if unidirectional==False: 
        ic.set("configuration","bidirectional")
    if conjugate==True:
        ic.set("conjugate",1)
    ic.set("name",name)
    ic.set("coupling coefficient 1", coupling_coefficient)
    ic.set("x position",0+xpos)
    ic.set("y position",0+ypos)
    

def connect(name1,port1,name2,port2):
    ic.connect(name1, f"port {port1}", name2, f"port {port2}")

def CW_laser(name,power,frequency=193.1e12,xpos=0,ypos=0):
    ic.addelement("CW laser")
    ic.set("name",name)
    ic.set("x position",0+xpos)
    ic.set("y position",0+ypos)
    ic.set("power",power) ### power must be set in W
    ic.set("frequency",frequency)

def power_meter(name,xpos=0,ypos=0):
    ic.addelement("optical power meter")
    ic.set("name",name)
    ic.set("x position",0+xpos)
    ic.set("y position",0+ypos)

def generate_mzi(theta,phi,i,j,xpos=0,ypos=0):
    """
    Generates and defines a full mzi of the following structure
    --- phi ---\   /----- 2theta -----\    /--- -theta ---
                ---                    ----
    -----------/   \------------------/    \--- -theta ---
    """

    phase_shifter(f"phi{i}{j}",phi,xpos=xpos,ypos=ypos)
    dir_coupler(f"coupler{i}{j}1",xpos=150+xpos,ypos=ypos)

    ic.connect(f"phi{i}{j}", "output",f"coupler{i}{j}1","input 1" )

    phase_shifter(f"theta{i}{j}",2*theta, xpos=300+xpos,ypos=ypos)
    
    ic.connect(f"coupler{i}{j}1", "output 1", f"theta{i}{j}", "input")
    
    dir_coupler(f"coupler{i}{j}2",xpos=450+xpos,conjugate=True,ypos=ypos)

    ic.connect(f"theta{i}{j}", "output", f"coupler{i}{j}2", "input 1")

    ic.connect(f"coupler{i}{j}1", "output 2", f"coupler{i}{j}2", "input 2")

    phase_shifter(f"otheta{i}{j}1",-theta, xpos=600+xpos,ypos=ypos)
    phase_shifter(f"otheta{i}{j}2",-theta, xpos=600+xpos,ypos=100+ypos)

    ic.connect(f"coupler{i}{j}2", "output 1", f"otheta{i}{j}1", "input")
    ic.connect(f"coupler{i}{j}2", "output 2", f"otheta{i}{j}2", "input")
    
def generate_lasers(vector,xpos=0,ypos=0):
    v=np.array(vector,dtype=float)
    for i in range (len(vector)):
        # print(i)
        CW_laser(f"CW{i}",v[i],xpos=xpos,ypos=ypos+i*300)

def bs_list_to_vectors(I): ### We are using this to adapt the code to the module interferometer, much lighter and simpler than strawberryfields
    """
    Convert I.BS_list into a Kx4 numeric matrix:
    columns = [mode1, mode2, theta, phi]
    Keeps modes as ints and angles as floats.
    """
    
    theta = np.array([bs.theta for bs in I.BS_list], dtype=float)
    phi   = np.array([bs.phi   for bs in I.BS_list], dtype=float)
    return theta,phi

def retrieve_position(element):
    """
    Returns the position of an element
    """
    return ic.getposition(element, "x"), ic.getposition(element, "y") 

def mzi_mesh(u,xpos=0,ypos=0,graph=False):
    """
    # Generates a MZI mesh, given a matrix
    
    # """
    ### Starts by calling strawberryfields to decompose the matrix
    I=itf.square_decomposition(u)
    
    thetas,phis=bs_list_to_vectors(I)

    if graph==True:
        I.draw()
        print(I.BS_list)

    dim=u.shape[0]
    k=0

    ### These are the two for loops that generate the MZIS in the order they are computed
    L = dim - 2
    count=0 ### this keeps the count for the list of phases
    pmcount=0
    if L < 0:
        return  

    for i in range(L + 1):  
        
        j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)

        ### These two ifs are just for the spatial arrangement of the mzis in interconnect
        if i==dim/2:
            k=k+1
        if i>dim/2:
            k=k+2

        for j in range(j_max + 1):

            generate_mzi(thetas[count],phis[count],i,j,xpos=i*1000-j*500-k*500+xpos,ypos=j*300+k*300+ypos)
            count=count+1
            

    ##### Instead of making the connections when the MZIs are being created, we are going to try to make the connections after they are created. 
    ##### It may take more time but it seems more straightforward.
    ##### Let's make the exact same loop but this time in each MZI we connect the two ouputs.

    if dim%2==0: ### Even and odd meshes are a bit different, this one is for even meshes
        for i in range(L + 1):  
            
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)


            for j in range(j_max + 1):
                
                if i<(L+1)//2: ### the odd iterations except the central one

                    if j==0: ### Condition for the upper row
                        ic.connect(f"otheta{i}{j}1", "output", f"phi{i+1}{j}","input")
                        ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}","input")

                    else: ### Condition for the interior elements of the odd iterations
                        ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                        ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}","input")

                if i==(L+1)//2: ### The central iteration

                    if j==0: ### First central element

                        ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j}","input")

                    elif j<j_max:
                        ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                        ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j}","input")

                    
                    if j==j_max:
                        ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                        ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-1}1","input 2")

                if i>(L+1)//2 and i<L:
                    
                    if j>0 and j<j_max: ### If j==0 the connections are open as it is the end of the mesh
                        ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                        ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j-1}","input")
                    
                    if j==j_max:
                        ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                        ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-2}1","input 2")

                if i==L and j!=0:
                    ### First no connection
                    ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                    
    if dim%2==1: ### Even and odd meshes are a bit different, this one is for odd meshes
            for i in range(L + 1):  
                
                j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)


                for j in range(j_max + 1):
                    
                    if i<(L+1)//2: ### the odd iterations except the central one

                        if j==0: ### Condition for the upper row
                            ic.connect(f"otheta{i}{j}1", "output", f"phi{i+1}{j}","input")
                            ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}","input")

                        else: ### Condition for the interior elements of the odd iterations
                            ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                            ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}","input")

                    if i==(L+1)//2: ### The central iteration

                        # if j==0: ### First central element

                        #     ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j}","input")

                        if j>0 and j<j_max:
                            ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                            ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j-1}","input")

                        
                        if j==j_max:
                            ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                            ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-2}1","input 2")

                    if i>(L+1)//2 and i<L:
                        
                        if j>0 and j<j_max: ### If j==0 the connections are open as it is the end of the mesh
                            ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                            ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j-1}","input")
                        
                        if j==j_max:
                            ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")
                            ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-2}1","input 2")

                    if i==L and j!=0:
                        ### First no connection
                        ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1","input 2")         

def generate_power_meters(dim):
    count=0
    ### Places the first power meter
    comp=f"otheta{(dim-1)//2}01"

    x,y=retrieve_position(comp)
    power_meter("pm0",x+100,y)
    ic.connect(comp,"output","pm0","input")
    count=count+1

    ### If dim is odd it needs to place another one
    if dim%2==1:
        comp=f"otheta{(dim-1)//2}02"
        x,y=retrieve_position(comp)
        power_meter("pm1",x+100,y)
        ic.connect(comp,"output","pm1","input")
        count=count+1


    ### This loop goes through the central MZIs
    for i in range(dim//2-1):

        comp=f"otheta{(dim-1)//2+i+1}01"
        x,y=retrieve_position(comp)
        power_meter(f"pm{count}",x+100,y)
        ic.connect(comp,"output",f"pm{count}","input")
        count=count+1

        comp=f"otheta{(dim-1)//2+i+1}02"
        x,y=retrieve_position(comp)
        power_meter(f"pm{count}",x+100,y)
        ic.connect(comp,"output",f"pm{count}","input")
        count=count+1

    ### Now only the last MZI is left
    comp=f"otheta{dim-2}12"
    x,y=retrieve_position(comp)
    power_meter(f"pm{count}",x+100,y)
    ic.connect(comp,"output",f"pm{count}","input")

def dBm_to_W(x):
    return 10**(x/10)/1000

def get_results(dim):
    return [(dBm_to_W(ic.getresult(f"pm{i}","sum/power")),ic.getresult(f"pm{i}","mode 1/angle")) for i in range(dim)]


def complex_to_polar(vec):
    return [(abs(z), cmath.phase(z)) for z in vec]

def redefine_MZI(i,j,theta,phi):
    ic.setnamed(f"phi{i}{j}","phase shift", phi)
    ic.setnamed(f"theta{i}{j}","phase shift",2*theta)
    ic.setnamed(f"otheta{i}{j}1","phase shift", -theta)
    ic.setnamed(f"otheta{i}{j}2","phase shift", -theta)

def redefine_mesh(u):
    dim=np.shape(u)[0]
    L=dim-2
    count=0
    I=itf.square_decomposition(u)
    thetas,phis=bs_list_to_vectors(I)
    for i in range(L + 1):  
        
        j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)

        for j in range(j_max + 1):
            redefine_MZI(i,j_max-j,thetas[count],phis[count])
            count=count+1

def MZI_multiplication(u,v,graph=False):
    dim=np.shape(u)[0]
    v_theoretical=u@v
    generate_lasers(v**2)
    mzi_mesh(u,xpos=100,graph=graph)
    j=0
    count=0
    ### Now let's connect the lasers with the mzis
    for i in range(dim//2):      
        ic.connect(f"CW{count}","output",f"phi{i}{j}","input")
        count+=1
        ic.connect(f"CW{count}","output",f"coupler{i}{j}1","input 2")
        count+=1
        j+=2

    ### If dim is odd we need an extra connection
    if dim%2==1:
        ic.connect(f"CW{count}","output",f"coupler{dim//2}{j-1}1","input 2")
    redefine_mesh(u)
    generate_power_meters(dim)
    ic.run()
    v_mesh=get_results(dim)
    v_res_sq=complex_to_polar(v_theoretical**2)
    print("Theory", v_res_sq,"\n","Mesh", v_mesh)

import numpy as np
from typing import Optional, Literal, Union

def random_vector(
    n: int,
    as_complex: bool = False,
    distribution: Literal['normal', 'uniform'] = 'normal',
    scale: float = 1.0,
    seed: Optional[int] = None,
    dtype: Optional[Union[np.dtype, str]] = None,
    normalize: Optional[Union[str, float]] = None,
) -> np.ndarray:
    """
    Generate a random vector (real or complex).

    Parameters
    ----------
    n : int
        Length of the vector.
    as_complex : bool, default False
        If True, returns a complex vector; otherwise real.
    distribution : {'normal', 'uniform'}, default 'normal'
        Distribution of samples:
          - 'normal': Gaussian.
              * Real: N(0, scale^2)
              * Complex: Re, Im ~ N(0, (scale^2)/2) → E[|z|^2] = scale^2 (circularly symmetric).
          - 'uniform': Each component drawn independently from [-scale, scale].
            (For complex, both real and imaginary parts use this range.)
    scale : float, default 1.0
        Scale parameter (std for 'normal'; half-range for 'uniform').
    seed : int or None, default None
        Seed for reproducibility.
    dtype : numpy dtype or str or None, default None
        Output dtype. Defaults to float64 for real and complex128 for complex.
    normalize : None, 'l2'/'unit', or float, default None
        Optional post-scaling:
          - 'l2' or 'unit': scale the vector to unit L2 norm.
          - float value p: scale so that mean power (mean(|x|^2)) equals p.

    Returns
    -------
    np.ndarray
        A vector of shape (n,) of type float or complex.
    """
    rng = np.random.default_rng(seed)

    if distribution == 'normal':
        if as_complex:
            s = scale / np.sqrt(2.0)  # so E|z|^2 = scale^2
            x = rng.normal(0.0, s, size=n)
            y = rng.normal(0.0, s, size=n)
            out = x + 1j * y
        else:
            out = rng.normal(0.0, scale, size=n)
    elif distribution == 'uniform':
        if as_complex:
            x = rng.uniform(-scale, scale, size=n)
            y = rng.uniform(-scale, scale, size=n)
            out = x + 1j * y
        else:
            out = rng.uniform(-scale, scale, size=n)
    else:
        raise ValueError("distribution must be 'normal' or 'uniform'")

    # Default dtypes
    if dtype is None:
        dtype = np.complex128 if as_complex else np.float64
    out = out.astype(dtype, copy=False)

    # Optional normalization
    if normalize is not None:
        if normalize in ('l2', 'unit'):
            norm = np.linalg.norm(out)
            if norm > 0:
                out = out / norm
        elif isinstance(normalize, (int, float)):
            target_power = float(normalize)
            power = np.mean(np.abs(out) ** 2)
            if power > 0:
                out = out * np.sqrt(target_power / power)
        else:
            raise ValueError("normalize must be None, 'l2'/'unit', or a number (target average power).")

    return out


# Inicializar INTERCONNECT con ruta relativa al archivo test.icp
# La ruta será relativa desde donde se ejecute el script
icp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.icp")
ic = lumapi.INTERCONNECT(icp_path, hide=True)