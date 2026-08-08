const SearchBar = () => {
    return (
        <div className="w-full rounded-3xl border border-slate-800 bg-slate-900/80 p-4 shadow-sm shadow-slate-950/30 backdrop-blur-sm sm:flex sm:items-center sm:justify-between">
            <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-300/80">Discover videos</p>
                <p className="mt-1 max-w-xl text-sm leading-6 text-slate-300 sm:text-base">
                    Search through the latest video releases and curated recommendations.
                </p>
            </div>
            <div className="mt-4 w-full sm:mt-0 sm:w-72">
                <label htmlFor="search" className="sr-only">Search videos</label>
                <div className="relative">
                    <input
                        id="search"
                        type="search"
                        placeholder="Search videos, artists, languages..."
                        className="w-full rounded-2xl border border-slate-700 bg-slate-950/90 px-4 py-3 pr-12 text-sm text-slate-100 placeholder:text-slate-500 focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
                    />
                    <span className="pointer-events-none absolute inset-y-0 right-4 flex items-center text-slate-500">
                        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 stroke-current" strokeWidth="2">
                            <path d="M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14Z" />
                            <path d="m16.5 16.5 4 4" strokeLinecap="round" />
                        </svg>
                    </span>
                </div>
            </div>
        </div>
    )
}
export default SearchBar;
