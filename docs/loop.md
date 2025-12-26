https://ghuntley.com/agent/ Thanks Geoff for the starter

## Base Loop

User Message -> Entry Agent -> Tool Calls -> User Message

All "interesting" stuff shall happen in tool calls. The tool call should never return to the entry agent, as that is an additional responsibility to the entry agent that is not entangled at all with its other tasks.

## Entry Agent

The entry agent just needs to be good at choosing tools. Its abilities are:
- making a tool call that returns directly to the user
- listing what it's able to do (`-h` essentially)