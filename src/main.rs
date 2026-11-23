use strata::prelude::*;

#[component]
fn App() -> View {
    let clicks = use_signal(0i32);
    let accent = use_signal(false);
    let note = use_signal(String::new());

    let c_inc = clicks.clone();
    let c_rst = clicks.clone();
    let a_tgl = accent.clone();
    let n_in = note.clone();

    let card_bg = if accent.get() {
        "bg-indigo-950/90 border-indigo-400/60"
    } else {
        "bg-neutral-900/95 border-neutral-700/80"
    };

    rsx! {
        <div class="w-full h-full bg-neutral-950 flex items-center justify-center p-8 text-white">
            <div class={format!("w-[560px] rounded-2xl border p-8 flex flex-col gap-6 {}", card_bg)}>
                <div class="flex flex-col gap-1">
                    <span class="text-xs uppercase tracking-widest text-indigo-400 font-semibold">
                        {"External MCP Test Target"}
                    </span>
                    <h1 class="text-2xl font-bold text-white">
                        {"Strata MCP Interactive Demo"}
                    </h1>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="rounded-xl bg-neutral-800/80 border border-neutral-700/60 p-4 flex flex-col gap-1">
                        <span class="text-xs text-neutral-400">{"Click Counter"}</span>
                        <span class="text-3xl font-bold text-emerald-400">
                            {format!("{}", clicks.get())}
                        </span>
                    </div>
                    <div class="rounded-xl bg-neutral-800/80 border border-neutral-700/60 p-4 flex flex-col gap-1">
                        <span class="text-xs text-neutral-400">{"Accent State"}</span>
                        <span class="text-xl font-semibold text-amber-300">
                            {if accent.get() { "Active" } else { "Default" }}
                        </span>
                    </div>
                </div>

                <div class="flex flex-row gap-3">
                    <button
                        id="btn-inc"
                        class="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm cursor-pointer"
                        onclick={move |_| c_inc.update(|v| *v += 1)}
                    >
                        <span>{"Increment +1"}</span>
                    </button>
                    <button
                        id="btn-accent"
                        class="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm cursor-pointer"
                        onclick={move |_| a_tgl.update(|v| *v = !*v)}
                    >
                        <span>{"Toggle Accent"}</span>
                    </button>
                    <button
                        id="btn-reset"
                        class="px-5 py-3 rounded-xl bg-neutral-800 hover:bg-neutral-700 border border-neutral-600 text-neutral-200 font-semibold text-sm cursor-pointer"
                        onclick={move |_| c_rst.set(0)}
                    >
                        <span>{"Reset"}</span>
                    </button>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="text-xs text-neutral-400">{"Input Box (click & type via MCP)"}</label>
                    <input
                        id="demo-input"
                        value={note.get()}
                        placeholder="Waiting for MCP typing..."
                        class="w-full px-4 py-3 rounded-xl bg-neutral-800 border border-neutral-600 text-white text-sm"
                        oninput={move |val: String| n_in.set(val)}
                    />
                    <span class="text-xs text-neutral-400">
                        {format!("Current input: \"{}\"", note.get())}
                    </span>
                </div>
            </div>
        </div>
    }
}

fn main() {
    let config = WindowConfig {
        title: "Strata MCP Demo".to_string(),
        width: 720,
        height: 520,
        ..Default::default()
    };

    if let Err(e) = strata::launch_with_config(App, config) {
        eprintln!("[mcp_demo] launch error: {e}");
    }
}
