"use client"

import { useState } from "react"

const RecommendMovies = () => {
  const [movieName, setMovieName] = useState("")
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const fetchRecommendations = async () => {
    if (!movieName) {
      setError("Please enter a movie name.")
      return
    }

    try {
      setLoading(true)
      setError("")

      const response = await fetch(`http://localhost:5000/recommend?movie=${encodeURIComponent(movieName)}`)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Something went wrong while fetching recommendations.")
      }

      const data = await response.json()

      setRecommendations(data || [])

      if (data.length === 0) {
        setError("No recommendations found for this movie. Please try another movie name.")
      }
    } catch (err) {
      console.error("Fetch error:", err)
      setError(err.message || "Failed to fetch recommendations. Please check if the server is running.")
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      fetchRecommendations()
    }
  }

  return (
    <div className="px-6 md:px-16 lg:px-24 xl:px-44 py-20">
      <h1 className="text-4xl font-bold mb-6 text-center text-white">Movie Recommendation System</h1>

      <div className="flex gap-2 mb-8 justify-center">
        <input
          type="text"
          value={movieName}
          onChange={(e) => setMovieName(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter a movie name (e.g., Inception)"
          className="flex-grow max-w-md border border-gray-400 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={fetchRecommendations}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Loading..." : "Recommend"}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 text-center max-w-xl mx-auto">
          {error}
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {recommendations.map((movie, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur border border-white/20 rounded-2xl overflow-hidden shadow-md hover:scale-[1.02] transition-transform duration-200 p-4"
            >
             

              <div className="text-white space-y-1">
                <h3 className="text-xl font-bold truncate">{movie.Name}</h3>
                <p className="text-sm text-gray-300">Genre: {movie.Genre || "Unknown"}</p>
                <p className="text-sm text-gray-300">Score: {movie.Score?.toFixed(1) || "N/A"}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {recommendations.length === 0 && !loading && !error && movieName && (
        <p className="text-gray-400 text-center mt-4">Enter a movie name and click "Recommend" to get suggestions.</p>
      )}
    </div>
  )
}

export default RecommendMovies
