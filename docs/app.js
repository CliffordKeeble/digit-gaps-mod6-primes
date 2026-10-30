// The page's own code. Python runs in worker.js; this file only talks to it.

// The keys race() returns and float_trap() returns. tests/ compares these two
// lists with RESULT_KEYS and TRAP_KEYS in docs/py/chebyshev_race.py.
const RESULT_KEYS = [
  "bound",
  "count_5_mod_6",
  "count_1_mod_6",
  "digits_5_mod_6",
  "digits_1_mod_6",
  "digit_difference",
  "larger",
  "seconds_sieve",
  "seconds_multiply",
  "seconds_digit_count",
  "seconds_total",
];
const TRAP_KEYS = [
  "float_route",
  "exact",
  "difference",
  "leading_digits_agree",
  "float_digits",
  "exact_digits",
  "float_mod_3",
  "exact_mod_3",
];

const LOAD_TIMEOUT_MS = 60_000;
const DEFAULT_BOUND = 1_000_000;

const statusLine = document.getElementById("status");
const failureLine = document.getElementById("failure");
const picker = document.getElementById("bound");
const resultsPanel = document.getElementById("results");
const trapPanel = document.getElementById("trap-numbers");

let worker = null;
let loadTimer = null;
let ready = false;
let loadSeconds = null;
let currentId = 0;
let busy = false;

const integerFormat = new Intl.NumberFormat("en-GB");

function twoSignificantFigures(seconds) {
  return `${Number(seconds.toPrecision(2))} s`;
}

function showFailure(stage, reason, bound = null) {
  console.error(`chebyshev demo: stage=${stage} bound=${bound} message=${reason}`);
  failureLine.hidden = false;
  failureLine.textContent =
    `Python could not load (${stage}: ${reason}). ` +
    "The figures on this page do not depend on it.";
  statusLine.textContent = "Python is not running.";
  setBusy(false);
  picker.disabled = true;
}

function setBusy(isBusy) {
  busy = isBusy;
  picker.disabled = isBusy || !ready;
}

function requestRace(bound) {
  currentId += 1;
  setBusy(true);
  resultsPanel.setAttribute("aria-busy", "true");
  resultsPanel.querySelector(".run-note").textContent =
    `Computing for primes up to ${integerFormat.format(bound)}…`;
  worker.postMessage({ type: "race", bound, id: currentId });
}

function renderResult(message) {
  const { id, bound, result } = message;
  // A reply is shown only if it answers the run in flight, for its own bound.
  if (id !== currentId || bound !== Number(picker.value)) {
    return;
  }
  for (const key of RESULT_KEYS) {
    if (!(key in result)) {
      showFailure("compute", `the reply is missing "${key}"`, bound);
      return;
    }
  }
  const larger = result.larger === "equal" ? "neither (equal)" : result.larger;
  const set = (name, text) => {
    resultsPanel.querySelector(`[data-field="${name}"]`).textContent = text;
  };
  set("count_5_mod_6", integerFormat.format(result.count_5_mod_6));
  set("count_1_mod_6", integerFormat.format(result.count_1_mod_6));
  set("digits_5_mod_6", integerFormat.format(result.digits_5_mod_6));
  set("digits_1_mod_6", integerFormat.format(result.digits_1_mod_6));
  set("digit_difference", integerFormat.format(result.digit_difference));
  set("larger", larger);
  set("load_time", twoSignificantFigures(loadSeconds));
  set("compute_time", twoSignificantFigures(result.seconds_total));
  resultsPanel.querySelector(".run-note").textContent =
    `Primes up to ${integerFormat.format(bound)}.`;
  resultsPanel.removeAttribute("aria-busy");
  setBusy(false);
}

function renderTrap(trap) {
  for (const key of TRAP_KEYS) {
    if (!(key in trap)) {
      showFailure("compute", `the trap reply is missing "${key}"`);
      return;
    }
  }
  const agree = trap.leading_digits_agree;
  const marked = (text) => {
    const agreeing = document.createElement("span");
    agreeing.className = "agree";
    agreeing.textContent = text.slice(0, agree);
    const rest = document.createElement("span");
    rest.textContent = text.slice(agree);
    const line = document.createElement("div");
    line.append(agreeing, rest);
    return line;
  };
  const rows = trapPanel.querySelector(".digits");
  rows.replaceChildren(marked(trap.exact), marked(trap.float_route));
  const set = (name, text) => {
    trapPanel.querySelector(`[data-field="${name}"]`).textContent = text;
  };
  set("leading_digits_agree", String(agree));
  set("difference", trap.difference);
  set("float_digits", String(trap.float_digits));
  set("exact_digits", String(trap.exact_digits));
  set("float_mod_3", String(trap.float_mod_3));
  set("exact_mod_3", String(trap.exact_mod_3));
}

function onReady(message) {
  ready = true;
  loadSeconds = message.loadSeconds;
  clearTimeout(loadTimer);
  const version = message.pythonVersion.split(" ")[0];
  statusLine.textContent =
    `Python ${version} on Pyodide ${message.pyodideVersion} · ` +
    `module sha256 ${message.moduleHash}`;
  statusLine.title = `sys.version: ${message.pythonVersion}`;
  picker.value = String(DEFAULT_BOUND);
  setBusy(false);
  requestRace(DEFAULT_BOUND);
}

function onWorkerMessage(event) {
  const message = event.data;
  if (message.type === "ready") {
    onReady(message);
  } else if (message.type === "result") {
    renderResult(message);
  } else if (message.type === "trap") {
    renderTrap(message.trap);
  } else if (message.type === "error") {
    showFailure(message.stage, message.message, message.bound);
  }
}

function startWorker() {
  statusLine.textContent = "Loading Python (about 6 MB, once)…";
  try {
    worker = new Worker("worker.js", { type: "module" });
  } catch (error) {
    showFailure("worker", error.message);
    return;
  }
  worker.onmessage = onWorkerMessage;
  worker.onerror = (event) => {
    showFailure("worker", event.message || "the worker script failed to run");
  };
  loadTimer = setTimeout(
    () => showFailure("timeout", "no answer within 60 seconds"),
    LOAD_TIMEOUT_MS,
  );
}

picker.addEventListener("change", () => {
  if (ready && !busy) {
    requestRace(Number(picker.value));
  }
});

picker.disabled = true;
startWorker();
