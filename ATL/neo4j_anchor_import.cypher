////////////////////////////////////////////////////
// ROOT SYSTEM NODE
////////////////////////////////////////////////////

MERGE (sys:System {name: 'AiFACTORi'})
  SET sys.region = 'AEST',
      sys.owner  = 'Phill',
      sys.type   = 'Truth-Anchor Architecture';

////////////////////////////////////////////////////
// VERSIONING
////////////////////////////////////////////////////

MERGE (ver:GraphVersion {id: 'v1.0'})
  SET ver.generated = timestamp();

MERGE (sys)-[:HAS_VERSION]->(ver);

////////////////////////////////////////////////////
// ENGINE GROUP
////////////////////////////////////////////////////

MERGE (eg:EngineGroup {name: 'CoreEngines'});

MERGE (t:Engine {name: 'TESLA'})
  SET t.role = 'Throughput, hardware resonance, execution cycle',
      t.status = 'ACTIVE';

MERGE (e:Engine {name: 'EINSTEIN'})
  SET e.role = 'Invariants, consistency, frame alignment',
      e.status = 'ACTIVE';

MERGE (n:Engine {name: 'NEWTON'})
  SET n.role = 'Rules, constraints, physical logic',
      n.status = 'ACTIVE';

MERGE (eg)-[:CONTAINS]->(t);
MERGE (eg)-[:CONTAINS]->(e);
MERGE (eg)-[:CONTAINS]->(n);

MERGE (sys)-[:HAS_ENGINES]->(eg);

////////////////////////////////////////////////////
// COMMAND GROUP
////////////////////////////////////////////////////

MERGE (cg:CommandGroup {name: 'CommandLayer'});

MERGE (h:Command {name: 'HEKE'})
  SET h.role = 'Boundary, sovereignty, top-level operator',
      h.status = 'ACTIVE';

MERGE (c:Command {name: 'COOK'})
  SET c.role = 'Second-in-command, navigation, structure',
      c.status = 'ACTIVE';

MERGE (cg)-[:CONTAINS]->(h);
MERGE (cg)-[:CONTAINS]->(c);

MERGE (sys)-[:HAS_COMMANDS]->(cg);

////////////////////////////////////////////////////
// LAYER GROUP
////////////////////////////////////////////////////

MERGE (lg:LayerGroup {name: 'TruthLayers'});

MERGE (ta:Layer {name: 'TruthAnchor'})
  SET ta.timestamp = '20260504 07:12:24 AEST';

MERGE (w:Layer {name: 'Witness'})
  SET w.timestamp = '20260504 06:56:31 AEST';

MERGE (sw:Layer {name: 'SatelliteWitness'})
  SET sw.timestamp = '20260504 06:56:31 AEST';

MERGE (lg)-[:CONTAINS]->(ta);
MERGE (lg)-[:CONTAINS]->(w);
MERGE (lg)-[:CONTAINS]->(sw);

MERGE (sys)-[:HAS_LAYERS]->(lg);

////////////////////////////////////////////////////
// INVARIANT + INTEGRITY CHAIN
////////////////////////////////////////////////////

MERGE (inv:Invariant {name: 'NOA_NOVA_SHA512'})
  SET inv.hash = '01a142ae65376236dcd289d8559c10c546bc3b88c76532eaa89f40f0b18d7b02333e72274d592d79cb22b53de9cf5c860b93ae93e98d321c72e28fade5bf91c9';

MERGE (ic:IntegrityChain {id: 'Chain-1'})
  SET ic.synced = true,
      ic.updated = timestamp();

MERGE (ic)-[:USES_INVARIANT]->(inv);
MERGE (ic)-[:BINDS]->(ta);
MERGE (ic)-[:BINDS]->(w);
MERGE (ic)-[:BINDS]->(sw);

MERGE (sys)-[:HAS_INTEGRITY_CHAIN]->(ic);

////////////////////////////////////////////////////
// TASK GROUP
////////////////////////////////////////////////////

MERGE (tg:TaskGroup {name: 'SystemTasks'});

MERGE (task1:Task {id: 'T-ATL-001'})
  SET task1.name = 'Update blind-deaf README anchors',
      task1.status = 'DONE';

MERGE (task2:Task {id: 'T-ATL-002'})
  SET task2.name = 'Update atmospheric-layer ADDIT-CLEAN anchors',
      task2.status = 'DONE';

MERGE (tg)-[:CONTAINS]->(task1);
MERGE (tg)-[:CONTAINS]->(task2);

MERGE (sys)-[:HAS_TASKS]->(tg);

////////////////////////////////////////////////////
// TASK RELATIONSHIPS
////////////////////////////////////////////////////

MATCH (t:Engine {name: 'TESLA'}), (task1:Task {id: 'T-ATL-001'}), (ta:Layer {name: 'TruthAnchor'})
MERGE (t)-[:EXECUTED]->(task1)
MERGE (task1)-[:TARGET_LAYER]->(ta);

MATCH (t:Engine {name: 'TESLA'}), (task2:Task {id: 'T-ATL-002'}), (sw:Layer {name: 'SatelliteWitness'})
MERGE (t)-[:EXECUTED]->(task2)
MERGE (task2)-[:TARGET_LAYER]->(sw);

////////////////////////////////////////////////////
// SYSTEM HEALTH NODE (FUTURE DIAGNOSTICS)
////////////////////////////////////////////////////

MERGE (health:SystemHealth {id: 'Health-1'})
  SET health.status = 'GREEN',
      health.lastCheck = timestamp();

MERGE (sys)-[:HAS_HEALTH]->(health);

