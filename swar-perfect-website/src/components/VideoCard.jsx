import Textbox from "./Textbox"

const VideoCard = (props) => {
    return (
        <article className="group overflow-hidden rounded-3xl border border-slate-800 bg-slate-950/80 shadow-xl shadow-slate-950/20 transition-all duration-300 hover:-translate-y-0.5 hover:border-violet-500/20 hover:bg-slate-900/90">
            <div className="relative overflow-hidden bg-slate-900">
                <div className="aspect-[16/9] w-full overflow-hidden">
                    <img
                        src={props.url}
                        alt={props.title}
                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                </div>
                <div className="absolute inset-x-4 bottom-4 rounded-2xl bg-gradient-to-t from-slate-950/90 via-slate-950/40 to-transparent px-4 py-3 text-slate-100 shadow-lg shadow-slate-950/30 backdrop-blur-sm">
                    <p className="text-sm font-semibold text-violet-200">{props.language}</p>
                    <h3 className="mt-1 text-base font-semibold text-white line-clamp-2">{props.title}</h3>
                </div>
            </div>
            <div className="space-y-4 p-5">
                <div className="space-y-2">
                    <p className="text-sm font-medium uppercase tracking-[0.18em] text-indigo-300/80">Overview</p>
                    <p className="text-sm leading-6 text-slate-300 line-clamp-3">
                        {props.description}
                    </p>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                    <Textbox title="Published" value={props.date_published} />
                    <Textbox title="Language" value={props.language} />
                </div>
            </div>
        </article>
    )
}
export default VideoCard