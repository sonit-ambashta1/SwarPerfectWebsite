import { useState } from "react"
import SearchBar from "../components/SearchBar"
import VideoCard from "../components/VideoCard";

const Dashboard = () => {
    // initially hardcoded data
    const videos = [
        {
            id: 1,
            url: "https://placehold.co/300x200",
            title: "Tum Hi Ho Karaoke",
            language: "Hindi",
            description: "A karaoke version of Tum Hi Ho.",
            date_published: "2026-08-01"
        },
        {
            id: 2,
            url: "https://placehold.co/300x200",
            title: "Perfect Karaoke",
            language: "English",
            description: "A karaoke version of Perfect.",
            date_published: "2026-08-03"
        },
        {
            id: 3,
            url: "https://placehold.co/300x200",
            title: "Channa Mereya Karaoke",
            language: "Hindi",
            description: "Karaoke track with lyrics.",
            date_published: "2026-08-05"
        }
    ];

    return (
        <main className="min-h-screen bg-slate-950 text-slate-100">
            <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-10 px-4 py-8 sm:px-6 lg:px-8">
                <header className="space-y-4">
                    <div className="max-w-3xl space-y-3">
                        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-violet-300/80">Swar Perfect Explorer</p>
                        <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                            Discover karaoke tracks by language, artist, and release date.
                        </h1>
                        <p className="max-w-2xl text-sm leading-7 text-slate-400 sm:text-base">
                            Browse latest video stories, filter by language, and preview content with a polished dashboard feel.
                        </p>
                    </div>
                    <SearchBar />
                </header>

                <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                    {videos.map((video) => (
                        <VideoCard
                            key={video.id}
                            url={video.url}
                            title={video.title}
                            language={video.language}
                            description={video.description}
                            date_published={video.date_published}
                        />
                    ))}
                </section>
            </div>
        </main>
    )
}
export default Dashboard