from simtk.openmm import app
import simtk.openmm as mm
from simtk import unit as u

#integrator_type = "langevin2fs"
integrator_type = "langevin1fs"

n_steps = 500000000
output_frequency = 500
dcd_frequency = 5000

friction = 1.0 / u.picoseconds
temperature = 300. * u.kelvin
pressure = 1.0 * u.atmospheres
barostat_frequency = 25
cutoff = 1.2 * u.nanometers  # Towards the high end to avoid cutoff artifacts.

ffxml_filename = "tip3p.xml"
ff = app.ForceField(ffxml_filename)

dcd_filename = "./water/production_%s.dcd" % integrator_type
log_filename = "./water/production_%s.log" % integrator_type

pdb = app.PDBFile("./tip3p.pdb")

topology = pdb.topology
positions = pdb.positions

system = ff.createSystem(topology, nonbondedMethod=app.PME, nonbondedCutoff=cutoff, constraints=app.HBonds)

integrators = {
"langevin2fs":mm.LangevinIntegrator(temperature, friction, 2.0 * u.femtoseconds), 
"langevin1fs":mm.LangevinIntegrator(temperature, friction, 1.0 * u.femtoseconds),
}

integrator = integrators[integrator_type]

system.addForce(mm.MonteCarloBarostat(pressure, temperature, barostat_frequency))

simulation = app.Simulation(topology, system, integrator)

simulation.context.setPositions(positions)
simulation.minimizeEnergy()
simulation.context.setVelocitiesToTemperature(temperature)

simulation.reporters.append(app.DCDReporter(dcd_filename, dcd_frequency))
simulation.reporters.append(app.StateDataReporter(open(log_filename, 'w'), output_frequency, step=True, time=True, temperature=True, speed=True, density=True))
print(integrator_type)
simulation.step(n_steps)
