"""
NEET syllabus topic catalogue with short, revision-friendly explanations.

Each topic carries:
  id          - stable slug used by the API and stored in the DB
  title       - display name
  unit        - NEET unit / chapter grouping
  weightage   - rough exam emphasis: 'high' | 'medium' | 'low'
  summary     - 2-4 sentence explanation shown on the topic card
  key_points  - bullet facts worth memorising

The explanations are deliberately concise. They are written to be accurate and
revision-friendly, but students should always cross-check against NCERT.
"""

SUBJECTS = {
    "physics": {"name": "Physics", "color": "#2563eb"},
    "chemistry": {"name": "Chemistry", "color": "#16a34a"},
    "biology": {"name": "Biology", "color": "#db2777"},
}


def _t(tid, title, unit, weightage, summary, key_points):
    return {
        "id": tid,
        "title": title,
        "unit": unit,
        "weightage": weightage,
        "summary": summary,
        "key_points": key_points,
    }


TOPICS = {
    "physics": [
        _t("phy-units", "Units, Dimensions & Measurement", "Unit & Measurement", "medium",
           "NEET tests whether you can express physical quantities in terms of the seven SI base units, "
           "check the dimensional consistency of equations, and propagate errors correctly. Dimensional "
           "analysis lets you verify formulae and derive relationships up to a dimensionless constant.",
           ["SI base units: metre, kilogram, second, ampere, kelvin, mole, candela.",
            "Dimensional formula of force is [M L T^-2]; of energy is [M L^2 T^-2].",
            "For z = a^p b^q / c^r, the fractional error is p(da/a) + q(db/b) + r(dc/c).",
            "Angles, trigonometric ratios and refractive index are dimensionless."]),

        _t("phy-kinematics", "Motion in a Straight Line & Plane", "Kinematics", "high",
           "Kinematics describes motion using displacement, velocity and acceleration without asking what "
           "causes it. For uniform acceleration the three equations of motion apply; for projectiles you "
           "split the problem into independent horizontal and vertical parts.",
           ["v = u + at, s = ut + at^2/2, v^2 = u^2 + 2as (constant a only).",
            "Slope of x-t graph gives velocity; slope of v-t graph gives acceleration; area under v-t gives displacement.",
            "Projectile: time of flight 2u sin(theta)/g, range u^2 sin(2 theta)/g, max height u^2 sin^2(theta)/2g.",
            "Relative velocity is vector subtraction: v_AB = v_A - v_B."]),

        _t("phy-laws-motion", "Laws of Motion", "Laws of Motion", "high",
           "Newton's three laws connect force to the rate of change of momentum. Free-body diagrams plus "
           "the resolution of forces along and perpendicular to the surface solve most problems involving "
           "inclines, pulleys and friction.",
           ["F = ma for constant mass; more generally F = dp/dt.",
            "Friction: f_s <= mu_s N (static, self-adjusting), f_k = mu_k N (kinetic).",
            "On an incline, the component of weight down the plane is mg sin(theta).",
            "Impulse J = F dt = change in momentum."]),

        _t("phy-work-energy", "Work, Energy & Power", "Work, Energy & Power", "high",
           "The work-energy theorem says net work equals the change in kinetic energy, which is often the "
           "fastest route to a speed. Conservative forces have a potential energy, and total mechanical "
           "energy is conserved when only they do work.",
           ["Work W = F s cos(theta); it can be negative or zero.",
            "Kinetic energy KE = (1/2)mv^2; potential energy of a spring U = (1/2)kx^2.",
            "Work-energy theorem: W_net = KE_final - KE_initial.",
            "Power P = dW/dt = F v; 1 horsepower ~ 746 W."]),

        _t("phy-rotation", "System of Particles & Rotational Motion", "Rotational Motion", "high",
           "Rotational motion mirrors linear motion with torque replacing force and moment of inertia "
           "replacing mass. The parallel-axis and perpendicular-axis theorems let you find the moment of "
           "inertia of composite bodies.",
           ["Torque tau = r x F; for a rigid body tau = I alpha.",
            "Moment of inertia: solid sphere (2/5)MR^2, disc (1/2)MR^2, rod about centre (1/12)ML^2.",
            "Angular momentum L = I omega is conserved when net external torque is zero.",
            "Rolling without slipping: v = omega R; total KE = (1/2)mv^2 + (1/2)I omega^2."]),

        _t("phy-gravitation", "Gravitation", "Gravitation", "medium",
           "Newton's law of gravitation gives an inverse-square force between point masses. Gravitational "
           "potential energy is negative, and escape velocity follows from setting total energy to zero.",
           ["F = G m1 m2 / r^2, with G = 6.67 x 10^-11 N m^2 kg^-2.",
            "Acceleration due to gravity g = GM/R^2; it decreases with altitude and depth.",
            "Orbital speed v = sqrt(GM/r); escape speed v_e = sqrt(2GM/R) = sqrt(2) v_orbital.",
            "Kepler's third law: T^2 proportional to a^3."]),

        _t("phy-thermo", "Thermodynamics", "Thermodynamics", "high",
           "Thermodynamics tracks energy transfer as heat and work in a system. The first law is energy "
           "conservation; the second law and entropy decide the direction of spontaneous change. Know the "
           "four ideal-gas processes and their P-V curves.",
           ["First law: dQ = dU + dW; for an ideal gas dU depends only on temperature.",
            "Isothermal: dU = 0, so Q = W. Adiabatic: Q = 0, so dU = -W; PV^gamma = constant.",
            "Carnot efficiency eta = 1 - T_cold/T_hot (temperatures in kelvin).",
            "Molar specific heats: C_p - C_v = R."]),

        _t("phy-current", "Current Electricity", "Current Electricity", "high",
           "Ohm's law and Kirchhoff's rules solve almost every DC circuit. For a cell, the terminal "
           "voltage falls below its EMF once current flows because of internal resistance.",
           ["V = IR; resistance R = rho L / A.",
            "Kirchhoff: junction rule (charge), loop rule (energy).",
            "Cells in series add EMFs; in parallel the net EMF and internal resistance use the reciprocal rule.",
            "Wheatstone bridge balances when P/Q = R/S."]),

        _t("phy-magnetism", "Moving Charges & Magnetism", "Magnetism", "high",
           "A moving charge feels a magnetic force perpendicular to both its velocity and the field. "
           "This bends charged particles into circles and underlies the force between current-carrying "
           "conductors.",
           ["Force F = q(v x B); magnitude qvB sin(theta).",
            "Radius of circular path r = mv/qB; cyclotron frequency independent of speed.",
            "Field of a long straight wire B = mu_0 I / (2 pi r).",
            "Ampere's circuital law relates the line integral of B to the enclosed current."]),

        _t("phy-optics", "Ray & Wave Optics", "Optics", "high",
           "Ray optics uses the mirror and lens formulae to locate images; wave optics explains "
           "interference, diffraction and polarisation. Total internal reflection needs light to travel "
           "from denser to rarer medium beyond the critical angle.",
           ["Mirror: 1/v + 1/u = 1/f. Lens: 1/v - 1/u = 1/f.",
            "Lens maker's formula: 1/f = (n-1)(1/R1 - 1/R2).",
            "Critical angle sin(C) = 1/n.",
            "Young's double slit: fringe width beta = lambda D / d."]),

        _t("phy-modern", "Dual Nature, Atoms & Nuclei", "Modern Physics", "high",
           "Light behaves as both wave and particle: photoelectric emission reveals the photon, while "
           "diffraction reveals the wave. Bohr's model quantises atomic energy levels, and nuclear "
           "stability follows from binding energy per nucleon.",
           ["Photon energy E = h nu = hc/lambda; photoelectric equation h nu = phi + KE_max.",
            "Bohr: angular momentum quantised as nh/2pi; energy of hydrogen levels E_n = -13.6/n^2 eV.",
            "de Broglie wavelength lambda = h/p.",
            "Mass-energy: E = mc^2; binding energy per nucleon peaks near iron-56."]),
    ],
    "chemistry": [
        _t("chem-atomic", "Atomic Structure", "Structure of Atom", "high",
           "The quantum-mechanical model describes electrons by orbitals and probability clouds rather "
           "than fixed paths. Quantum numbers label an orbital and constrain how many electrons it holds.",
           ["Quantum numbers: n (shell), l (shape), m_l (orientation), m_s (spin).",
            "Orbitals fill by Aufbau order with the n+l rule; Hund's rule keeps unpaired spins parallel.",
            "Max electrons in a shell = 2n^2; in an orbital = 2.",
            "Heisenberg uncertainty principle: position and momentum cannot both be exact."]),

        _t("chem-bonding", "Chemical Bonding & Molecular Structure", "Chemical Bonding", "high",
           "Bonds form to lower energy, giving atoms noble-gas-like configurations. VSEPR predicts shape "
           "from electron-pair repulsion, while hybridisation explains bond angles and geometry.",
           ["Ionic bonds need large electronegativity difference; covalent bonds share electrons.",
            "VSEPR: lone pairs repel more than bond pairs, reducing bond angles (e.g. H2O 104.5 deg).",
            "Hybridisation: sp (linear 180), sp2 (trigonal 120), sp3 (tetrahedral 109.5).",
            "Bond order from molecular orbital theory explains O2 paramagnetism."]),

        _t("chem-thermo", "Thermodynamics & Thermochemistry", "Thermodynamics", "high",
           "Chemical thermodynamics predicts whether a reaction is spontaneous through the sign of the "
           "Gibbs energy change. Enthalpy, entropy and temperature together decide feasibility.",
           ["Enthalpy change dH = dU + (dn)RT for gases.",
            "Gibbs energy dG = dH - T dS; spontaneous when dG < 0.",
            "Hess's law: enthalpy is path-independent.",
            "Standard enthalpy of formation of an element in its standard state is zero."]),

        _t("chem-equilibrium", "Equilibrium & Ionic Equilibrium", "Equilibrium", "high",
           "Reversible reactions settle at equilibrium where forward and reverse rates match. Le "
           "Chatelier's principle predicts how the position shifts with concentration, pressure or "
           "temperature changes.",
           ["Equilibrium constant K depends only on temperature.",
            "Le Chatelier: a system opposes the imposed change.",
            "For weak acids K_a = [H+][A-]/[HA]; pH = -log[H+].",
            "Buffer (Henderson-Hasselbalch): pH = pKa + log([salt]/[acid])."]),

        _t("chem-electro", "Electrochemistry", "Redox & Electrochemistry", "high",
           "Electrochemistry links redox reactions to electrical energy. Galvanic cells convert chemical "
           "energy to electricity; electrolytic cells do the reverse. Cell potential follows from standard "
           "reduction potentials.",
           ["Cell EMF E_cell = E_cathode - E_anode (reduction potentials).",
            "Nernst equation: E = E0 - (0.059/n) log Q at 298 K.",
            "Gibbs energy dG = -nFE; positive E_cell means spontaneous.",
            "Faraday's laws relate charge passed to amount of substance deposited."]),

        _t("chem-kinetics", "Chemical Kinetics", "Chemical Kinetics", "high",
           "Kinetics studies reaction rates and the steps by which reactions occur. The order of a "
           "reaction is experimental, while the molecularity of an elementary step is theoretical.",
           ["Rate = k[A]^x[B]^y; x + y is the overall order.",
            "First-order half-life t_1/2 = 0.693/k, independent of initial concentration.",
            "Arrhenius equation: k = A e^(-Ea/RT).",
            "Catalysts lower activation energy without changing dG or equilibrium."]),

        _t("chem-solutions", "Solutions", "Solutions", "medium",
           "Solutions are homogeneous mixtures whose properties depend on solute concentration. Colligative "
           "properties depend only on the number of solute particles, not their identity.",
           ["Molarity = moles/L of solution; molality = moles/kg of solvent.",
            "Raoult's law: partial vapour pressure proportional to mole fraction.",
            "Colligative properties: relative lowering of vapour pressure, boiling point elevation, "
            "freezing point depression, osmotic pressure.",
            "van't Hoff factor i accounts for association/dissociation."]),

        _t("chem-organic", "Hydrocarbons", "Hydrocarbons", "high",
           "Hydrocarbons contain only carbon and hydrogen and are the backbone of organic chemistry. "
           "Alkanes are saturated; alkenes and alkynes are unsaturated and far more reactive at the "
           "multiple bond.",
           ["Alkanes undergo free-radical substitution; alkenes/alkynes undergo addition.",
            "Markovnikov's rule: H adds to the carbon with more hydrogens.",
            "Benzene is aromatic: delocalised 6 pi electrons, undergoes electrophilic substitution.",
            "Tollens' and Baeyer's reagents distinguish aldehydes and unsaturation."]),

        _t("chem-biomolecules", "Biomolecules & Polymers", "Biomolecules", "medium",
           "Biomolecules are the molecules of life: carbohydrates, proteins, nucleic acids and vitamins. "
           "Their structure determines function, from enzyme catalysis to genetic storage.",
           ["Carbohydrates: monosaccharides (glucose) join by glycosidic bonds.",
            "Proteins are polymers of amino acids linked by peptide bonds; structure has 4 levels.",
            "DNA and RNA are polynucleotides; DNA has deoxyribose and thymine.",
            "Enzymes are highly specific biological catalysts (lock-and-key / induced fit)."]),
    ],
    "biology": [
        _t("bio-cell", "Cell: Structure & Function", "Cell Structure", "high",
           "The cell is the basic unit of life. Prokaryotes lack a true nucleus and membrane-bound "
           "organelles; eukaryotes compartmentalise functions into organelles.",
           ["Mitochondria are the powerhouse (ATP); chloroplasts carry out photosynthesis.",
            "Ribosomes are the site of protein synthesis; ER and Golgi process and package proteins.",
            "Cell theory: all organisms are made of cells, the cell is the unit of life, all cells arise from pre-existing cells.",
            "Fluid mosaic model describes the plasma membrane."]),

        _t("bio-biomolecules", "Biomolecules", "Biomolecules", "high",
           "Living systems are built from a small set of macromolecules. Structure-function relationships "
           "and the role of enzymes as catalysts are frequently tested.",
           ["Proteins: amino acids joined by peptide bonds; primary to quaternary structure.",
            "Enzymes lower activation energy; activity affected by pH and temperature.",
            "Nucleic acids: DNA (double helix) and RNA (several types).",
            "Lipids are not polymers but are essential (membranes, energy storage)."]),

        _t("bio-plant-physio", "Plant Physiology", "Plant Physiology", "medium",
           "Plants photosynthesise, respire, transport water and nutrients, and respond to their "
           "environment. Photosynthesis converts light energy into chemical energy in the chloroplast.",
           ["Light reaction produces ATP and NADPH; Calvin cycle fixes CO2.",
            "Transpiration pull drives water up the xylem; translocation moves sugars in the phloem.",
            "C3, C4 and CAM pathways differ in photorespiration handling.",
            "Plant hormones: auxin, gibberellin, cytokinin, abscisic acid, ethylene."]),

        _t("bio-human-physio", "Human Physiology", "Human Physiology", "high",
           "Human physiology covers how body systems maintain homeostasis. Digestion, respiration, "
           "circulation, excretion and neural control are all heavily weighted in NEET.",
           ["Neuron conducts impulses; synapse transmits via neurotransmitters.",
            "Heart has four chambers; SA node is the natural pacemaker.",
            "Nephron is the functional unit of the kidney; urine formation has filtration, reabsorption, secretion.",
            "Hormones from endocrine glands regulate metabolism, growth and reproduction."]),

        _t("bio-reproduction", "Reproduction", "Reproduction", "high",
           "Reproduction ensures continuity of species. Both plants and humans show sexual reproduction, "
           "and reproductive health is a NEET priority.",
           ["Human male: sperm produced in seminiferous tubules; female: ovum in ovary.",
            "Menstrual cycle ~28 days; ovulation around day 14.",
            "Double fertilisation and triple fusion are unique to angiosperms.",
            "Contraception and STI awareness are part of reproductive health."]),

        _t("bio-genetics", "Genetics & Evolution", "Genetics", "high",
           "Genetics explains inheritance through genes and chromosomes. Mendel's laws, the chromosomal "
           "basis of inheritance and molecular genetics form a large share of NEET Biology.",
           ["Mendel's laws: dominance, segregation, independent assortment.",
            "Sex-linked inheritance: colour blindness and haemophilia are X-linked.",
            "DNA replication is semi-conservative; central dogma: DNA -> RNA -> protein.",
            "Evolution: natural selection, Hardy-Weinberg equilibrium."]),

        _t("bio-biotech", "Biotechnology & Applications", "Biotechnology", "medium",
           "Biotechnology uses living systems to make useful products. Recombinant DNA technology, PCR "
           "and genetic engineering are core topics.",
           ["Restriction enzymes cut DNA at specific sites; ligase joins fragments.",
            "PCR amplifies DNA using primers and Taq polymerase.",
            "Bt cotton and insulin production are classic applications.",
            "Bioreactors scale up bioprocesses."]),

        _t("bio-ecology", "Ecology & Environment", "Ecology", "high",
           "Ecology studies interactions between organisms and their environment. Population, ecosystem "
           "and biodiversity questions are reliable scorers in NEET.",
           ["Food chains and webs; energy flow follows the 10% law.",
            "Ecological pyramids: number, biomass, energy.",
            "Biodiversity hotspots in India: Western Ghats, Himalaya, Indo-Burma, Sundaland.",
            "In-situ vs ex-situ conservation."]),

        _t("bio-human-health", "Human Health & Disease", "Human Health", "high",
           "This unit covers pathogens, immunity, and the diseases they cause. AIDS, cancer and "
           "immunity are frequently asked.",
           ["Pathogens: bacteria, viruses, fungi, protozoa, helminths.",
            "Immunity: innate vs acquired; active vs passive.",
            "AIDS caused by HIV (retrovirus) attacking helper T-cells.",
            "Cancer: uncontrolled cell division; benign vs malignant tumours."]),
    ],
}


def all_topics():
    out = []
    for subj, items in TOPICS.items():
        for t in items:
            out.append({**t, "subject": subj})
    return out


def get_topic(topic_id):
    for subj, items in TOPICS.items():
        for t in items:
            if t["id"] == topic_id:
                return {**t, "subject": subj}
    return None
