
'''Elements module'''

from sqlalchemy import Column, Integer, String, Float, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import os
from operator import attrgetter

Base = declarative_base()

#create the database and get the session

def get_session():
    '''Return the database session connection.'''

    dbpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "elements.db")
    engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=False)
    db_session =  sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return db_session()

class Element(Base):
    '''
    Chemical element.

    Attributes:
      annotation : str
        Annotations regarding the data
      atomic_number : int
        Atomic number
      atomic_radius : float
        Atomic radius in pm
      atomic_volume : float
        Atomic volume in cm3/mol
      block : int
        Block in periodic table
      boiling_point : float
        Boiling temperature in K
      category : str
        Category in the periodic table
      covalent_radius : float
        Covalent radius in pm
      density : float
        Density at 295K in g/cm3 respectively g/L
      description : str
        Short description of the element
      dipole_polarizability : float
        Dipole polarizability in atomic units from P. Schwerdtfeger "Table of
        experimental and calculated static dipole polarizabilities for the
        electronic ground states of the neutral elements (in atomic units)",
        February 11, 2014
      electron_affinity : float
        Electron affinity in eV
      electronegativity : float
        Electronegativity (Pauling scale)
      electronic_configuration : str
        Ground state electron configuration
      evaporation_heat : float
        Evaporation heat in kJ/mol
      fusion_heat : float
        Fusion heat in kJ/mol
      group : int
        Group in periodic table
      lattice_constant : float
        Lattice constant in ang
      lattice_structure : str
        Lattice structure code
      mass : float
        Relative atomic mass. Ratio of the average mass of atoms
        of the element to 1/12 of the mass of an atom of 12C
      melting_point : float
        Melting temperature in K
      name : str
        Name in english
      period : int
        Period in periodic table
      series : int
        Index to chemical series
      specific_heat : float
        Specific heat in J/g mol @ 20 C
      symbol : str of length 1 or 2
        Chemical symbol
      thermal_conductivity : float
        Thermal conductivity in @/m K @25 C
      vdwrad : float
        Van der Waals radius in Angstrom
      oxistates : str
        Oxidation states
      ionenergy : tuple
        Ionization energies in eV parsed from
        http://physics.nist.gov/cgi-bin/ASD/ie.pl on April 13, 2015
    '''

    __tablename__ = 'elements'

    annotation = Column(String)
    atomic_number = Column(Integer, primary_key=True)
    atomic_radius = Column(Float)
    atomic_volume = Column(Float)
    block = Column(String)
    boiling_point = Column(Float)
    covalent_radius = Column(Float)
    density = Column(Float)
    description = Column(String)
    dipole_polarizability = Column(Float)
    electron_affinity = Column(Float)
    electronegativity = Column(Float)
    electronic_configuration = Column(String)
    evaporation_heat = Column(Float)
    fusion_heat = Column(Float)
    group = relationship("Group", uselist=False)
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    lattice_constant = Column(Float)
    lattice_structure = Column(String)
    mass = Column(Float)
    melting_point = Column(String)
    name = Column(String)
    period = Column(Integer)
    _series_id = Column("series_id", Integer, ForeignKey("series.id"))
    _series = relationship("Series", uselist=False)
    series = association_proxy("_series", "name")
    specific_heat = Column(Float)
    symbol = Column(String)
    thermal_conductivity = Column(Float)
    vdw_radius = Column(Float)

    ionization_energies = relationship("IonizationEnergy")
    oxidation_states = relationship("OxidationState")
    isotopes = relationship("Isotope")

    def ionization_energies_dict(self):
        '''
        Return a dict with ionization degree as key and ionization energy in eV
        as values.
        '''

        return {ie.degree:ie.energy for ie in self.ionization_energies}

    @hybrid_property
    def electrons(self):
        '''Return the number of electrons.'''

        return self.atomic_number

    @hybrid_property
    def protons(self):
        '''Return the number of protons.'''

        return self.atomic_number

    @hybrid_property
    def neutrons(self):
        '''Return the number of neutrons of the most abundant natural stable isotope.'''

        return self.mass_number - self.protons

    @hybrid_property
    def mass_number(self):
        '''Return the mass number of the most abundant natural stable isotope.'''

        return max(self.isotopes, key=attrgetter("abundance")).mass_number

    @hybrid_property
    def exact_mass(self):
        '''Return the mass calculated from isotopic composition.'''

        return sum(iso.mass * iso.abundance for iso in self.isotopes)

    def __str__(self):
        return "{0} {1} {2}".format(self.atomic_number, self.symbol, self.name)

    def __repr__(self):
        return "%s(\n%s)" % (
                 (self.__class__.__name__),
                 ' '.join(["\t%s=%r,\n" % (key, getattr(self, key))
                            for key in sorted(self.__dict__.keys())
                            if not key.startswith('_')]))


class IonizationEnergy(Base):
    '''
    Ionization energy of an element

    Attributes:
      atomic_number : int
        Atomic number
      degree : int
        Degree of ionization with respect to neutral atom
      energy : float
        Ionization energy in eV parsed from
        http://physics.nist.gov/cgi-bin/ASD/ie.pl on April 13, 2015
    '''

    __tablename__ = 'ionizationenergies'

    id = Column(Integer, primary_key=True)
    atomic_number = Column(Integer, ForeignKey("elements.atomic_number"))
    degree = Column(Integer)
    energy = Column(Float)

    def __str__(self):

        return "{0:5d} {1:5d} {2:10.5f}".format(self.atomic_number, self.degree, self.energy)

    def __repr__(self):

        return "<IonizationEnergy(atomic_number={a:5d}, degree={d:3d}, energy={e:10.5f})>".format(
               a=self.atomic_number, d=self.degree, e=self.energy)

class OxidationState(Base):
    '''
    Oxidation states of an element

    Attributes:
      atomic_number : int
        Atomic number
      oxidation_state : int
        Oxidation state
    '''

    __tablename__ = 'oxidationstates'

    id = Column(Integer, primary_key=True)
    atomic_number = Column(Integer, ForeignKey("elements.atomic_number"))
    oxidation_state = Column(Integer)

    def __repr__(self):

        return "<OxidationState(atomic_number={a:5d}, oxidation_state={o:5d})>".format(
               a=self.atomic_number, o=self.oxidation_state)

class Group(Base):
    '''Name of the group in the periodic table.'''

    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True)
    symbol = Column(String)
    name = Column(String)

    def __repr__(self):

        return "<Group(symbol={s:s}, name={n:s})>".format(
               s=self.symbol, n=self.name)

class Series(Base):
    '''
    Name of the series in the periodic table.

    Attributes:
      name : str
        Name of the series
    '''

    __tablename__ = 'series'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):

        return "<Series(name={n:s})>".format(n=self.name)

class Isotope(Base):
    '''
    Isotope

    Attributes:
      atomic_number : int
        Atomic number
      mass : float
        Mass of the isotope
      abundance : float
        Abundance of the isotope
      mass_number : int
        Mass number of the isotope
    '''

    __tablename__ = "isotopes"

    id = Column(Integer, primary_key=True)
    atomic_number = Column(Integer, ForeignKey("elements.atomic_number"))
    mass = Column(Float)
    abundance = Column(Float)
    mass_number = Column(Integer)

    def __str__(self):

        return "{0:5d} {1:10.5f} {2:6.2f}% {3:5d}".format(
                self.atomic_number, self.mass, self.abundance*100, self.mass_number)

    def __repr__(self):

        return "<Isotope(mass={}, abundance={}, mass_number={})>".format(
               self.mass, self.abundance, self.mass_number)

def element(ids):
    '''
    Based on the type of the `ids` identifier return either an ``Element``
    object from the database, or a list of ``Element`` objects if the `ids` is
    a list or a tuple of identifiers. Valid identifiers for an element are:
    *name*, *symbol*, *atomic number*.
    '''

    if isinstance(ids, (list, tuple)):
        return [get_element(i) for i in ids]
    elif isinstance(ids, (str, int)):
        return get_element(ids)
    else:
        raise ValueError("Expected a <list>, <tuple>, <str> or <int>, got: {0:s}".format(type(ids)))

def get_element(ids):
    '''
    Return an element from the database based on the `ids` identifier passed.
    Valid identifiers for an element are: *name*, *symbol*, *atomic number*.
    '''

    session = get_session()

    if isinstance(ids, str):
        if len(ids) <= 3 and ids.lower() != "tin":
            return session.query(Element).filter(Element.symbol == ids).one()
        else:
            return session.query(Element).filter(Element.name == ids).one()
    elif isinstance(ids, int):
        return session.query(Element).filter(Element.atomic_number == ids).one()
    else:
        raise ValueError("Expecting a <str> or <int>, got: {0:s}".format(type(ids)))


