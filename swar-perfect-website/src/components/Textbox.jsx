const Textbox = (props) => {
    return (
        <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                {props.title}
            </p>
            <p className="text-sm leading-6 text-slate-200">
                {props.value}
            </p>
        </div>
    )
}
export default Textbox;