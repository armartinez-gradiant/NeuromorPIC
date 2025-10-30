import numpy as np
from scipy.stats import ortho_group
from scipy.stats import unitary_group

import interferometer as itf
import cmath
import math

import mathfs # type: ignore

import os
import sys
from lumapi_loader import lumapi
if lumapi is None:
    sys.exit("No se pudo cargar lumapi.")

#### some more function definitions

def phase_shifter(name,angle,ic,unidirectional=True,xpos=0,ypos=0):
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

def dir_coupler(name,ic,coupling_coefficient=0.5,unidirectional=True,conjugate=False,xpos=0,ypos=0):
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
    

def connect(ic,name1,port1,name2,port2):
    ic.connect(name1, f"port {port1}", name2, f"port {port2}")

def CW_laser(name,power,ic,phase=0,frequency=193.1e12,xpos=0,ypos=0):
    ic.addelement("CW laser")
    ic.set("name",name)
    ic.set("x position",0+xpos)
    ic.set("y position",0+ypos)
    ic.set("power",power) ### power must be set in W
    ic.set("frequency",frequency)
    ic.set("phase",phase)

def power_meter(name,ic,xpos=0,ypos=0):
    ic.addelement("optical power meter")
    ic.set("name",name)
    ic.set("x position",xpos)
    ic.set("y position",ypos)

def amplifier(name,gain,ic,xpos=0,ypos=0, noise=False):
    ic.addelement("optical amplifier")
    ic.set("name",name)
    ic.set("x position",xpos)
    ic.set("y position",ypos)
    if gain>1:
        ic.set("gain",10*math.log10(gain))
    else:
        ic.set("gain",0)
    ic.set("enable noise", noise)

def generate_mzi(theta,phi,i,j,k,ic,xpos=0,ypos=0,diagonal=False,delta1=0,delta2=0):
    """
    Generates and defines a full mzi of the following structure
    --- phi ---\   /----- 2theta -----\    /--- -theta ---
                ---                    ----
    -----------/   \------------------/    \--- -theta ---

    Delta1 and delta2 are used at the end of the mesh, to implement the final phases of the decomposition

    """
    if diagonal==False:
        phase_shifter(f"phi{i}{j}{k}",phi,ic,xpos=xpos,ypos=ypos)
        dir_coupler(f"coupler1{i}{j}{k}",ic,xpos=150+xpos,ypos=ypos,conjugate=False)

        ic.connect(f"phi{i}{j}{k}", "output",f"coupler1{i}{j}{k}","input 1" )

        phase_shifter(f"theta{i}{j}{k}",2*theta,ic, xpos=300+xpos,ypos=ypos)
        
        ic.connect(f"coupler1{i}{j}{k}", "output 1", f"theta{i}{j}{k}", "input")
        
        dir_coupler(f"coupler2{i}{j}{k}",ic,xpos=450+xpos,conjugate=True,ypos=ypos)

        ic.connect(f"theta{i}{j}{k}", "output", f"coupler2{i}{j}{k}", "input 1")

        ic.connect(f"coupler1{i}{j}{k}", "output 2", f"coupler2{i}{j}{k}", "input 2")

        phase_shifter(f"otheta1{i}{j}{k}",delta1,ic, xpos=600+xpos,ypos=ypos)
        phase_shifter(f"otheta2{i}{j}{k}",delta2,ic, xpos=600+xpos,ypos=100+ypos)

        ic.connect(f"coupler2{i}{j}{k}", "output 1", f"otheta1{i}{j}{k}", "input")
        ic.connect(f"coupler2{i}{j}{k}", "output 2", f"otheta2{i}{j}{k}", "input")

    if diagonal==True:  ### This is a special case for the MZI of the diagonals, which don't require as many phase shifters
        dir_coupler(f"coupler1{i}{j}{k}",ic,xpos=xpos,ypos=ypos)
        phase_shifter(f"theta{i}{j}{k}",2*theta,ic, xpos=150+xpos,ypos=ypos)

        ic.connect(f"coupler1{i}{j}{k}", "output 1",f"theta{i}{j}{k}","input")

        dir_coupler(f"coupler2{i}{j}{k}",ic,xpos=xpos+300,ypos=ypos,conjugate=True)

        ic.connect(f"coupler1{i}{j}{k}", "output 2",f"coupler2{i}{j}{k}","input 2")
        ic.connect(f"theta{i}{j}{k}","output",f"coupler2{i}{j}{k}", "input 1")
        
        phase_shifter(f"phase{i}{j}{k}", -theta,ic, xpos=xpos+600,ypos=ypos)
        ic.connect(f"coupler2{i}{j}{k}","output 1",f"phase{i}{j}{k}","input")

    

    
def generate_lasers(vector,angles,ic,xpos=0,ypos=0):
    v=np.array(vector,dtype=float)
    for i in range (len(vector)):
        CW_laser(f"CW{i}",v[i],ic,phase=angles[i],xpos=xpos,ypos=ypos+i*300)

def redefine_lasers(vector,angles,ic):
    v=np.array(vector,dtype=float)
    for i in range (len(vector)):
        ic.setnamed(f"CW{i}","power", v[i])
        ic.setnamed(f"CW{i}","phase", angles[i])

def bs_list_to_vectors(I): ### We are using this to adapt the code to the module interferometer, much lighter and simpler than strawberryfields
    """
    Convert I.BS_list into a Kx4 numeric matrix:
    columns = [mode1, mode2, theta, phi]
    Keeps modes as ints and angles as floats.
    """
    
    theta = np.array([bs.theta for bs in I.BS_list], dtype=float)
    phi   = np.array([bs.phi   for bs in I.BS_list], dtype=float)
    mode1=np.array([bs.mode1   for bs in I.BS_list], dtype=float)
    mode2=np.array([bs.mode2   for bs in I.BS_list], dtype=float)
    return theta,phi,mode1,mode2

def theoretical_mzi_mult(u,v):
    ### Multiplies the vector by each mzi theoretically, used mainly for testing
    I=itf.square_decomposition(u)
    a=bs_list_to_vectors(I)
    dim=np.shape(v)[0]
    nmzis=dim*(dim-1)//2

    for i in range(nmzis):
        v=mathfs.T_mn(a[0][i],a[1][i],int(a[2][i]-1),int(a[3][i]-1),dim)@v

    return v

def retrieve_position(element,ic):
    """
    Returns the position of an element
    """
    return ic.getposition(element, "x"), ic.getposition(element, "y") 

def mzi_mesh(u,ic,k,xpos=0,ypos=0,graph=False,testing=False):
    """
    # Generates a MZI mesh, given a matrix
    
    # """
    ### Starts by calling strawberryfields to decompose the matrix
    I=itf.square_decomposition(u)
    deltas=I.output_phases
    thetas,phis,mode1,mode2=bs_list_to_vectors(I)
    print(deltas)

    if graph==True:
        I.draw()
        print(I.BS_list)

    dim=u.shape[0]
    l=0
    
    ### These are the two for loops that generate the MZIS in the order they are computed
    L = dim - 2
    count=0 ### this keeps the count for the list of phases
    if L < 0:
        return  

    for i in range(L + 1):  
        
        j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)

        ### These two ifs are just for the spatial arrangement of the mzis in interconnect
        if i==dim/2:
            l=l+1
        if i>dim/2:
            l=l+2

        for j in range(j_max + 1):

            generate_mzi(thetas[count],phis[count],i,j,k,ic=ic,xpos=i*1000-j*500-l*500+xpos,ypos=j*300+l*300+ypos)
            
            

    ##### Instead of making the connections when the MZIs are being created, we are going to try to make the connections after they are created. 
    ##### It may take more time but it seems more straightforward.
    ##### Let's make the exact same loop but this time in each MZI we connect the two ouputs.

    if dim%2==0: ### Even and aodd meshes are a bit different, this one is for even meshes
        for i in range(L + 1):  
            
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)


            for j in range(j_max + 1):
                
                if i<(L+1)//2: ### the odd iterations except the central one

                    if j==0: ### Condition for the upper row
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"phi{i+1}{j}{k}","input")
                        ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j+1}{k}","input")

                    else: ### Condition for the interior elements of the odd iterations
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                        ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j+1}{k}","input")

                if i==(L+1)//2: ### The central iteration

                    if j==0: ### First central element

                        ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j}{k}","input")

                    elif j<j_max:
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                        ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j}{k}","input")

                    
                    if j==j_max:
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                        ic.connect(f"otheta2{i}{j}{k}", "output", f"coupler1{i+1}{j-1}{k}","input 2")

                if i>(L+1)//2 and i<L:
                    
                    if j>0 and j<j_max: ### If j==0 the connections are open as it is the end of the mesh
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                        ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j-1}{k}","input")
                    
                    if j==j_max:
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                        ic.connect(f"otheta2{i}{j}{k}", "output", f"coupler1{i+1}{j-2}{k}","input 2")

                if i==L and j!=0:
                    ### First no connection
                    ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                    
    if dim%2==1: ### Even and odd meshes are a bit different, this one is for odd meshes
            for i in range(L + 1):  
                
                j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)


                for j in range(j_max + 1):
                    
                    if i<(L+1)//2: ### the odd iterations except the central one

                        if j==0: ### Condition for the upper row
                            ic.connect(f"otheta1{i}{j}{k}", "output", f"phi{i+1}{j}{k}","input")
                            ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j+1}{k}","input")

                        else: ### Condition for the interior elements of the odd iterations
                            ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                            ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j+1}{k}","input")

                    if i==(L+1)//2: ### The central iteration

                        # if j==0: ### First central element

                        #     ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j+1}{k}","input")

                        if j>0 and j<j_max:
                            ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                            ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j-1}{k}","input")

                        
                        if j==j_max and j-2>=0:
                            ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                            ic.connect(f"otheta2{i}{j}{k}", "output", f"coupler1{i+1}{j-2}{k}","input 2")

                    if i>(L+1)//2 and i<L:
                        
                        if j>0 and j<j_max: ### If j==0 the connections are open as it is the end of the mesh
                            ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                            ic.connect(f"otheta2{i}{j}{k}", "output", f"phi{i+1}{j-1}{k}","input")
                        
                        if j==j_max:
                            ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")
                            ic.connect(f"otheta2{i}{j}{k}", "output", f"coupler1{i+1}{j-2}{k}","input 2")

                    if i==L and j!=0:
                        ### First no connection
                        ic.connect(f"otheta1{i}{j}{k}", "output", f"coupler1{i}{j-1}{k}","input 2")         
def generate_power_meters(dim,ic,k,diagonal=False): ### needs adaptation to ks
    if diagonal==False:
        count=0
        ### Places the first power meter
        comp=f"otheta1{(dim-1)//2}0{k}"

        x,y=retrieve_position(comp,ic)
        power_meter(f"pm0{k}",ic,x+100,y)
        ic.connect(comp,"output",f"pm0{k}","input")
        count=count+1

        ### If dim is odd it needs to place another one
        if dim%2==1:
            comp=f"otheta2{(dim-1)//2}0{k}"
            x,y=retrieve_position(comp,ic)
            power_meter(f"pm1{k}",ic,x+100,y)
            ic.connect(comp,"output",f"pm1{k}","input")
            count=count+1


        ### This loop goes through the central MZIs
        for i in range(dim//2-1):

            comp=f"otheta1{(dim-1)//2+i+1}0{k}"
            x,y=retrieve_position(comp,ic)
            power_meter(f"pm{count}{k}",ic,x+100,y)
            ic.connect(comp,"output",f"pm{count}{k}","input")
            count=count+1

            comp=f"otheta2{(dim-1)//2+i+1}0{k}"
            x,y=retrieve_position(comp,ic)
            power_meter(f"pm{count}{k}",ic,x+100,y)
            ic.connect(comp,"output",f"pm{count}{k}","input")
            count=count+1

        ### Now only the last MZI is left
        comp=f"otheta2{dim-2}1{k}"
        x,y=retrieve_position(comp,ic)
        power_meter(f"pm{count}{k}",ic,x+100,y)
        ic.connect(comp,"output",f"pm{count}{k}","input")

    else: ### When diagonal=True, the function is adapted to the diagonal
        for i in range(dim):
            comp=f"coupler2{i}0{k}"

            x,y=retrieve_position(comp,ic)
            power_meter(f"pm{i}{k}",ic,x+100,y)
            ic.connect(comp,"output 1",f"pm{i}{k}","input")


def get_results(dim,k,ic):
        return [(mathfs.dBm_to_W(ic.getresult(f"pm{i}{k}","sum/power")),ic.getresult(f"pm{i}{k}","mode 1/angle")) for i in range(dim)]


def redefine_MZI(i,j,k,theta,phi,ic,delta1=0,delta2=0):
    ic.setnamed(f"phi{i}{j}{k}","phase shift", phi)
    ic.setnamed(f"theta{i}{j}{k}","phase shift",2*theta)
    ic.setnamed(f"otheta1{i}{j}{k}","phase shift", -theta+delta1)
    ic.setnamed(f"otheta2{i}{j}{k}","phase shift", -theta+delta2)

def redefine_mesh(u,k,ic):
    dim=np.shape(u)[0]
    L=dim-2
    count=0
    dcount=0
    I=itf.square_decomposition(u)
    thetas,phis,mode1,mode2=bs_list_to_vectors(I)
    deltas=I.output_phases
    for i in range(L + 1):  
        
        j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)

        for j in range(j_max + 1):
            redefine_MZI(i,j_max-j,k,thetas[count],phis[count],ic)
            
            ### The end phases are re-redefined in case they are necessary, their distribution is different for ood and even meshes
            if dim%2==1:
                if j==j_max and i>=dim//2 and i<dim-1:
                    redefine_MZI(i,j_max-j,k,thetas[count],phis[count],ic=ic,delta1=deltas[dcount],delta2=deltas[dcount+1])
                    print(dcount,deltas[dcount],deltas[dcount+1])
                    dcount=dcount+2

                if j==j_max-1 and i==dim-2:
                    redefine_MZI(i,j_max-j,k,thetas[count],phis[count],ic=ic,delta2=deltas[dcount])
                    # print("ole")

            else: ### even meshes
                if j==j_max and i==dim//2-1:
                    print(i,j,"www")
                    redefine_MZI(i,j_max-j,k,thetas[count],phis[count],ic=ic,delta1=deltas[dcount])
                    dcount=dcount+1

                if j==j_max and i>=dim//2 and i<dim-1:
                    redefine_MZI(i,j_max-j,k,thetas[count],phis[count],ic=ic,delta1=deltas[dcount],delta2=deltas[dcount+1])
                    print(dcount,deltas[dcount],deltas[dcount+1])
                    dcount=dcount+2

                if j==j_max-1 and i==dim-2:
                    redefine_MZI(i,j_max-j,k,thetas[count],phis[count],ic=ic,delta2=deltas[dcount])
                    print("ole")    

            count=count+1


def MZI_multiplication(u,v,ic,create_circuit,graph=False):
    dim=np.shape(u)[0]
    v_theoretical=u@v
    k=0
    if create_circuit==True:
        generate_lasers(v**2,np.angle(v),ic)
        mzi_mesh(u,ic=ic,k=k,xpos=100,graph=graph)
        j=0
        count=0
        ### Now let's connect the lasers with the mzis
        for i in range(dim//2):      
            ic.connect(f"CW{count}","output",f"phi{i}{j}{k}","input")
            count+=1
            ic.connect(f"CW{count}","output",f"coupler1{i}{j}{k}","input 2")
            count+=1
            j+=2

        ### If dim is odd we need an extra connection
        if dim%2==1:
            ic.connect(f"CW{count}","output",f"coupler{dim//2}{j-1}1","input 2")
        redefine_mesh(u,ic)
        generate_power_meters(dim,ic)

    else: ### If the circuit doesn't need to be generated, it is just redefined
        redefine_lasers(v**2,np.angle(v),ic)
        redefine_mesh(u,ic)

    ic.run()
    v_mesh=get_results(dim,ic)
    ic.switchtodesign() ### once the results are saved, it switches back to design mode, so that there are no problems when reusing the file
    ic.save()
    v_res_sq=mathfs.complex_to_polar(v_theoretical**2)
    print("Theory", v_res_sq,"\n","Mesh", v_mesh)


import os
from pathlib import Path
from typing import Optional, Tuple, Union


def create_matrix_icp(
    m: int,
    n: Optional[int] = None,
    folder: Union[str, os.PathLike] = ".",
    ic=None,
    hide: bool = True,
) -> Tuple[str, bool]:
    """
    Ensure an INTERCONNECT project file named matrix{m}x{n}.icp exists.
    If it doesn't, create it by saving the current (empty) project.

    Args:
        m (int): number of rows (or 'n' if you want a square n×n matrix).
        n (Optional[int]): number of columns. If None, defaults to m (square).
        folder (str | PathLike): target folder (default ".").
        ic: optional Lumerical INTERCONNECT handle to reuse. If None, a
            temporary session is created and closed.
        hide (bool): whether to hide the INTERCONNECT GUI when creating a session.

    Returns:
        Tuple[str, bool]: (absolute_path_to_icp, created_flag)
            - created_flag is True if the file was created now, False if it already existed.

    Raises:
        ValueError: if m/n are not positive integers.
        RuntimeError: if lumapi is unavailable when a new session is needed.
    """
    # Backward compatibility: if n not provided, assume square m×m
    if n is None:
        n = m

    if not (isinstance(m, int) and isinstance(n, int) and m > 0 and n > 0):
        raise ValueError("m and n must be positive integers")

    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    path = str((folder_path / f"matrix{m}x{n}.icp").resolve())

    # If already exists, nothing to do
    if os.path.exists(path):
        return path, False

    owns_session = ic is None
    if owns_session:
        if lumapi is None:
            raise RuntimeError(
                "lumapi (Lumerical INTERCONNECT Python API) is required to create new projects."
            )
        ic = lumapi.INTERCONNECT(hide=hide)  # set hide=False for debugging

    try:
        # Fresh INTERCONNECT opens with a blank project; just save it
        ic.save(path)
    finally:
        if owns_session:
            ic.close()

    return path, True


##### Here we will implement functions for decomposing any matrix into MZIs, through svd

from scipy.linalg import svd
from scipy.linalg import diagsvd
# a=10*np.random.rand(2,3)
# U, S, Vt =svd(a)
# print(a, U, S, Vt)





def mzi_diagonal(v,k,ic,xpos=0,ypos=0):
    ### it is defined from a vector as it is a diagonal matrix
    dim=np.shape(v)[0]
    theta=np.zeros(dim)
    for i in range(dim):
        if abs(v[i])<=1:
            theta[i]=np.arccos(v[i])
        else:
            theta[i]=0
    for i in range(dim):
        generate_mzi(theta[i],phi=0,i=i,j=0,k=k,ic=ic,xpos=xpos,ypos=ypos+i*300,diagonal=True)

def generate_amplifiers(d,k,ic,xpos=0,ypos=0):
    dim=np.shape(d)[0]
    for i in range(dim):
        amplifier(f"amp{i}{k}",d[i],ic,xpos=xpos,ypos=ypos+i*300,noise=False)

def connect_mesh_to_output(k,ic,dimV,dimS,output):
    count=0
    comp=f"otheta1{(dimV-1)//2}0{k}"
    ic.connect(comp,"output",f"{output}0{k}","input")
    count=count+1

    if dimV%2==1:
        comp=f"otheta2{(dimV-1)//2}0{k}"
        ic.connect(comp,"output",f"{output}1{k}","input")
        count=count+1

    for i in range(dimV//2-1):
        if count<dimS:
            comp=f"otheta1{(dimV-1)//2+i+1}0{k}"
            ic.connect(comp,"output",f"{output}{count}{k}","input")
            count=count+1

        if count<dimS:
            comp=f"otheta2{(dimV-1)//2+i+1}0{k}"
            ic.connect(comp,"output",f"{output}{count}{k}","input")
            count=count+1

    ### Last MZI
    if count<dimS:
        comp=f"otheta2{dimV-2}1{k}"
        ic.connect(comp,"output",f"{output}{count}{k}","input")

def connect_diagonal_to_mesh(k,ic,dimS):
    ### It is equivalent to connecting the lasers at the beginning of the circuit
    j=0
    count=0
    ### Now let's connect the lasers with the mzis
    for i in range(dimS//2):      
        ic.connect(f"phase{count}0{k}","output",f"phi{i}{j}{k+1}","input")
        count+=1
        ic.connect(f"phase{count}0{k}","output",f"coupler1{i}{j}{k+1}","input 2")
        count+=1
        j+=2

    ### If dim is odd we need an extra connection
    if dimS%2==1:
        ic.connect(f"phase{count}0{k}","output",f"coupler1{dimS//2}{j-1}{k+1}","input 2")


def general_mzi_mesh(a,k,ic,xpos=0,ypos=0):
    #### Checks if a is unitary, if it is, it calls mzi_mesh directly
    if mathfs.is_unitary(a):
        mzi_mesh(a)
    
    else:
        #### First we decompose the matrix with SVD
        U, S, Vh =svd(a)

        dimU=np.shape(U)[0]
        dimS=np.shape(S)[0]
        dimVh=np.shape(Vh)[0]

        ### First Mesh with vh
        mzi_mesh(Vh,ic,k,xpos=xpos,ypos=ypos,graph=False)
        ### Then the diagonal
        generate_amplifiers(S**2,k,ic,xpos=xpos+300+1100*dimVh//2,ypos=0)
        mzi_diagonal(S,k+1,ic,xpos=xpos+500+1100*dimVh//2,ypos=0)

        ### Connect amps to mzis
        for i in range(dimS):
            ic.connect(f"amp{i}{k}", "output",f"coupler1{i}0{k+1}","input 1")


        connect_mesh_to_output(k,ic,dimV=dimVh,dimS=dimS,output="amp")

        ### Second Mesh
        mzi_mesh(U,ic,k+2,xpos=xpos+700+1100*dimVh//2+600,ypos=ypos)

        ### connect diagonal to second mesh
        connect_diagonal_to_mesh(k+1,ic,dimS=dimS)

def connect_inputs_to_mesh(dimU,ic,k=0,input="CW"):
    j=0
    count=0
    if input=="CW":
        l=""
    else:
        l=k-1
    ### Now let's connect the lasers with the mzis
    for i in range(dimU//2):      
        ic.connect(f"{input}{count}{l}","output",f"phi{i}{j}{k}","input")
        count+=1
        ic.connect(f"{input}{count}{l}","output",f"coupler1{i}{j}{k}","input 2")
        count+=1
        j+=2

    ### If dim is odd we need an extra connection
    if dimU%2==1:
        ic.connect(f"{input}{count}{l}","output",f"coupler1{dimU//2}{j-1}{k}","input 2")

def general_MZI_multiplication(u,v,ic,graph=False):
    create_circuit=True
    dimU,dimV=np.shape(u)
    v_theoretical=u@v
    U, S, Vh= svd(u)
    vth1=Vh@v
    vth2=diagsvd(S,dimU,dimV)@vth1
    vth3=U@vth2

    k=0
    if create_circuit==True:
        generate_lasers(v**2,np.angle(v),ic)
        general_mzi_mesh(u,k,ic=ic,xpos=100)
        
        connect_inputs_to_mesh(dimU,ic,k=0,input="CW")

        redefine_mesh(Vh,0,ic)
        redefine_mesh(U,2,ic)
        generate_power_meters(dimV,ic,0)
        generate_power_meters(dimU,ic,1,diagonal=True)
        generate_power_meters(dimU,ic,2)

    else: ### If the circuit doesn't need to be generated, it is just redefined
        redefine_lasers(v**2,np.angle(v),ic)
        redefine_mesh(u,ic)

    ic.run()
    v_mesh1=get_results(dimV,0,ic)
    v_mesh2=get_results(dimU,1,ic)
    v_mesh3=get_results(dimU,2,ic)
    # ic.switchtodesign() ### once the results are saved, it switches back to design mode, so that there are no problems when reusing the file
    # ic.save()
    v_res1=mathfs.complex_to_polar(vth1,square_modulus=True)
    v_res2=mathfs.complex_to_polar(v_theoretical,square_modulus=True)
    print(
        "Initial vector",v,"\n",
        "Theory", v_res2,"\n",
        "Mesh", v_mesh3,"\n",
        "Theory SVD",vth3**2,"\n",
        "Diagonal SVD",vth2**2,"\n",
        "Diagonal Mesh", v_mesh2,"\n",
        "Int theory",v_res1,"\n",
        "Int mesh", v_mesh1
          )
    
def generate_non_linearities(dim,k,ic,xpos=0,ypos=0):
    """
    This function creates the non-linear layer after a linear one. 
    It requires having in the element library the scripted element "Optical Relu"
    """
    for i in range(dim):
        ic.addelement("optical relu")
        ic.set("name",f"relu{i}{k}")
        ic.set("x position",xpos)
        ic.set("y position",ypos+i*200)

def neural_network_layer(a,k,ic,xpos=0,ypos=0):
    """
    This function creates each linear and non-linear layer
    """
    dims=np.shape(a)
    general_mzi_mesh(a,k,ic,xpos=xpos,ypos=ypos)
    mesh_pos=retrieve_position(f"otheta1{dims[0]//2}0{k+2}",ic)
    generate_non_linearities(dims[0],k+2,ic,xpos=mesh_pos[0]+200)

    connect_mesh_to_output(k+2,ic,dimV=dims[0],dimS=dims[0],output="relu")
 
def optical_neural_network(v,m,ic,inference=False):
    """
    Args:
    v: Input vector for inference
    m: Set of matrices of the neural network, following the order of the layers
    ic: interconnect handle
    """

    dim=[np.shape(m[i]) for i in range(len(m))]
    print(dim[0][1])
    create_circuit=True
    xpos=0
    generate_lasers(v**2, np.angle(v),ic)

    neural_network_layer(m[0],k=0,ic=ic,xpos=300)

    connect_inputs_to_mesh(dim[0][1],ic,k=0,input="CW")

    for i in range(1,len(m)):
        x,y=retrieve_position(f"relu0{3*i-1}",ic)
        neural_network_layer(m[i],k=3*i,ic=ic,xpos=x+300)
        connect_inputs_to_mesh(dim[i][1],ic,k=3*i,input="relu")
                     




    