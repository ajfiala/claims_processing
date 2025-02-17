## Insurance Claims Processing

This is a proof-of-concept which demonstrates how AI agents with structured outputs
can be used to simplify the user experience of traditional claims processing applications.

This application ingests loss descriptions and automatically categorizes them into a certain line of business (in this case home or auto).
It then retrieves the pre-defined business rule questions for the claim type. The agent then answers these questions based on its analysis of the loss description
and returns the completed processed claim object in a structured JSON format. The goal is to simplify the user experience so that claimants only need to provide a
loss description instead of answering many pre-defined questions on the UI. 

# Dependencies
Ensure that you have astral's uv installed https://astral.sh/

# UI
`npm i`
`npm run dev`

## Add components
`npx shadcn@canary add textarea`
