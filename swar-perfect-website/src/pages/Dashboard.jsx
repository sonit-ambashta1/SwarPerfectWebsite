import { useState, useEffect } from "react"
import SearchBar from "../components/SearchBar"
import VideoCard from "../components/VideoCard";

const Dashboard = () => {
    // initially hardcoded data
    const [videos, setVideos] = useState([]);

    async function fetchVideos(){
        const link = import.meta.env.VITE_CLOUDFRONT_DISTRIBUTION_LINK || "/filtered_videos.json";

        let video_list = await fetch(link).then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        console.log(video_list);

        const normalizedVideos = video_list.map((video) => ({
            id: video.video_id ?? video.id,
            url: video.thumbnail_url ?? video.url,
            title: video.title,
            description: video.description,
            date_published: video.publish_date ?? video.date_published,
        }))

        console.log(normalizedVideos);
        setVideos(normalizedVideos);
    }
    
    useEffect(() => {
        fetchVideos();
    }, []);

    return (
        <main className="min-h-screen bg-slate-950 text-slate-100">
            <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-10 px-4 py-8 sm:px-6 lg:px-8">
                <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/5 px-4 py-2">
                    <span className="h-2 w-2 rounded-full bg-violet-400"></span>
                    <span className="text-sm text-slate-300">
                        {videos.length} tracks available
                    </span>
                </div>
                <header className="space-y-4">
                    <div className="max-w-3xl space-y-3">
                        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-violet-300/80">Swar Perfect</p>
                        <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                            Discover karaoke tracks by language, artist, and release date.
                        </h1>
                        <p className="max-w-2xl text-sm leading-7 text-slate-400 sm:text-base">
                            Searchbar coming soon.
                        </p>
                    </div>
                    {/* Disabled SearchBar for now, as the search functionality is not yet implemented. */}
                </header>
                <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                    {videos.map((video) => (
                        <VideoCard
                            key={video.id}
                            url={video.url}
                            title={video.title}
                            description={video.description}
                            date_published={video.date_published}
                            id={video.id}
                        />
                    ))}
                </section>
            </div>
        </main>
    )
}
export default Dashboard