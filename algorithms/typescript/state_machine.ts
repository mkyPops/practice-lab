/**
 * A generic, typed finite state machine.
 * Supports per-transition guard conditions and per-state entry/exit hooks.
 * States and events are constrained to string literal unions for type safety.
 */

type TransitionConfig<S extends string, E extends string, C> = {
  target: S;
  guard?: (context: C) => boolean;
  action?: (context: C) => void;
};

type StateConfig<S extends string, E extends string, C> = {
  onEnter?: (context: C) => void;
  onExit?: (context: C) => void;
  on?: Partial<Record<E, TransitionConfig<S, E, C>>>;
};

type MachineConfig<S extends string, E extends string, C> = {
  initial: S;
  context: C;
  states: Record<S, StateConfig<S, E, C>>;
};

class FiniteStateMachine<S extends string, E extends string, C> {
  private _state: S;
  private readonly context: C;
  private readonly states: Record<S, StateConfig<S, E, C>>;

  constructor(config: MachineConfig<S, E, C>) {
    this._state = config.initial;
    this.context = config.context;
    this.states = config.states;
  }

  get state(): S {
    return this._state;
  }

  /** Returns true if the event has a defined, guard-passing transition from the current state. */
  canFire(event: E): boolean {
    const transition = this.states[this._state].on?.[event];
    if (!transition) return false;
    return transition.guard ? transition.guard(this.context) : true;
  }

  /** Attempts to fire an event, running exit/action/entry hooks in order. Returns true on success. */
  fire(event: E): boolean {
    const currentConfig = this.states[this._state];
    const transition = currentConfig.on?.[event];
    if (!transition) return false;
    if (transition.guard && !transition.guard(this.context)) return false;

    currentConfig.onExit?.(this.context);
    transition.action?.(this.context);

    this._state = transition.target;
    this.states[this._state].onEnter?.(this.context);
    return true;
  }
}

// --- Example usage ---

type TrafficLightState = "red" | "yellow" | "green";
type TrafficLightEvent = "TIMER" | "EMERGENCY";
type TrafficLightContext = { emergencyOverride: boolean };

const trafficLight = new FiniteStateMachine<
  TrafficLightState,
  TrafficLightEvent,
  TrafficLightContext
>({
  initial: "red",
  context: { emergencyOverride: false },
  states: {
    red: {
      onEnter: () => console.log("Entering red"),
      on: {
        TIMER: { target: "green" },
        EMERGENCY: {
          target: "red",
          guard: (ctx) => ctx.emergencyOverride,
        },
      },
    },
    green: {
      onEnter: () => console.log("Entering green"),
      on: { TIMER: { target: "yellow" } },
    },
    yellow: {
      onEnter: () => console.log("Entering yellow"),
      onExit: () => console.log("Exiting yellow"),
      on: { TIMER: { target: "red" } },
    },
  },
});

trafficLight.fire("TIMER"); // red -> green
trafficLight.fire("TIMER"); // green -> yellow
console.log(trafficLight.state); // "yellow"
