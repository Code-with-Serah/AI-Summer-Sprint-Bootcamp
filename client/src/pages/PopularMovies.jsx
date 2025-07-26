import React, { useEffect, useState } from 'react';
import { StarIcon, HeartIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import MovieRecommendation from '../components/RecommendationPage';

const API_KEY = '0dd467261d53da92bf4ccb13b38e9623';

const PopularMovies = () => {
  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchGenres() {
      const res = await fetch(
        `https://api.themoviedb.org/3/genre/movie/list?api_key=${API_KEY}&language=en-US`
      );
      const data = await res.json();
      // Convert array to object: { 28: 'Action', 12: 'Adventure', ... }
      const genreMap = {};
      data.genres.forEach((genre) => {
        genreMap[genre.id] = genre.name;
      });
      setGenres(genreMap);
    }

    async function fetchPopularMovies() {
      const res = await fetch(
        `https://api.themoviedb.org/3/movie/popular?api_key=${API_KEY}&language=en-US&page=1`
      );
      const data = await res.json();
      setMovies(data.results);
    }

    fetchGenres();
    fetchPopularMovies();
  }, []);

  return (
  <>
    <div className="grid mt-15 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-6 p-6">
      {movies.map((movie) => (
        <div
          key={movie.id}
          className="flex flex-col justify-between p-3 bg-gray-800 rounded-2xl hover:-translate-y-1 transition duration-300 w-66"
        >
          <img
            onClick={() => {
              navigate(`/movie/${movie.id}`);
              scrollTo(0, 0);
            }}
            src={`https://image.tmdb.org/t/p/w500${movie.backdrop_path || movie.poster_path}`}
            alt={movie.title}
            className="rounded-lg h-52 w-full object-cover cursor-pointer"
          />

          <p className="font-semibold mt-2 truncate">{movie.title}</p>

          <p className="text-sm text-gray-400 mt-2">
            {movie.release_date?.slice(0, 4)} &bull;{' '}
            {movie.genre_ids
              .slice(0, 2)
              .map((id) => genres[id])
              .filter(Boolean)
              .join(' | ')}
          </p>

          <div className="flex items-center justify-between mt-4 pb-3">
            <button className="p-2 text-xs bg-gray-700 hover:bg-gray-600 transition rounded-full font-medium cursor-pointer">
              <HeartIcon className="w-4 h-4 text-red-500" />
            </button>

            <p className="flex items-center gap-1 text-sm text-gray-400 mt-1 pr-1">
              <StarIcon className="w-4 h-4 text-yellow-400 fill-yellow-400" />
              {movie.vote_average.toFixed(1)}
            </p>
          </div>
        </div>
      ))}
    </div>

    {/* Call the MovieRecommendation component at the end */}
    <MovieRecommendation />
  </>
);
}
export default PopularMovies;
