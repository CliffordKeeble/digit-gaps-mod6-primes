// Runs Python (Pyodide) off the page's thread. A module worker: it imports
// pyodide.mjs, loads docs/py/chebyshev_race.py (the file the tests check, not a
// copy), and answers {type: "race", bound} with the module's own race().
// Every failure is posted as {type: "error", stage, bound, message}.

const PYODIDE_VERSION = "314.0.7";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
const MODULE_URL = new URL("py/chebyshev_race.py", self.location.href);

let chebyshevRace = null;

function fail(stage, error, bound = null, id = null) {
  const message = error instanceof Error ? error.message : String(error);
  self.postMessage({ type: "error", stage, bound, id, message });
}

async function sha256Prefix(bytes) {
  if (!self.crypto || !self.crypto.subtle) {
    return "unavailable (needs https or localhost)";
  }
  const digest = await self.crypto.subtle.digest("SHA-256", bytes);
  const hex = Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
  return hex.slice(0, 12);
}

function toPlainObject(proxy) {
  const plain = proxy.toJs({ dict_converter: Object.fromEntries });
  proxy.destroy();
  return plain;
}

async function start() {
  let pyodide;
  try {
    const { loadPyodide } = await import(`${PYODIDE_URL}pyodide.mjs`);
    pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  } catch (error) {
    return fail("load", error);
  }
  // performance.now() in a worker counts from the worker's creation.
  const loadSeconds = performance.now() / 1000;

  let moduleBytes;
  try {
    const response = await fetch(MODULE_URL, { cache: "no-cache" });
    if (!response.ok) {
      throw new Error(`py/chebyshev_race.py: HTTP ${response.status}`);
    }
    moduleBytes = new Uint8Array(await response.arrayBuffer());
  } catch (error) {
    return fail("fetch", error);
  }

  let pythonVersion;
  let moduleHash;
  try {
    pyodide.FS.mkdirTree("/app/py");
    pyodide.FS.writeFile("/app/py/chebyshev_race.py", moduleBytes);
    pyodide.runPython("import sys; sys.path.insert(0, '/app/py')");
    chebyshevRace = pyodide.pyimport("chebyshev_race");
    pythonVersion = pyodide.runPython("sys.version");
    moduleHash = await sha256Prefix(moduleBytes);
  } catch (error) {
    return fail("import", error);
  }

  self.postMessage({
    type: "ready",
    pythonVersion,
    pyodideVersion: pyodide.version,
    pyodideVersionPinned: PYODIDE_VERSION,
    moduleHash,
    loadSeconds,
  });

  try {
    self.postMessage({ type: "trap", trap: toPlainObject(chebyshevRace.float_trap()) });
  } catch (error) {
    fail("compute", error);
  }
}

self.onmessage = (event) => {
  const { type, bound, id } = event.data;
  if (type !== "race" || chebyshevRace === null) {
    return;
  }
  try {
    // The bound goes in as a value; no Python source is built from input.
    const result = toPlainObject(chebyshevRace.race(bound));
    self.postMessage({ type: "result", id, bound, result });
  } catch (error) {
    fail("compute", error, bound, id);
  }
};

start();
