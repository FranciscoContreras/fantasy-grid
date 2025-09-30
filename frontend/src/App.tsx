import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-4xl font-bold mb-8">Fantasy Grid - Player Analysis</h1>
        <p className="text-muted-foreground">
          Fantasy football player recommendation app with AI-powered insights.
        </p>
        <p className="mt-4 text-sm text-muted-foreground">
          Frontend setup complete. Install dependencies with <code className="bg-muted px-2 py-1 rounded">npm install</code>
        </p>
      </div>
    </div>
  )
}

export default App
