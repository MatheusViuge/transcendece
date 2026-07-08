import type { TColumns } from "./types";

export function THead ({ columns } : { columns: TColumns }) {
    return (
        <thead className="bg-white sticky top-0 border-b border-solid border-overlay z-10">
            <tr>
                { Object.keys(columns).map((key) => (
                    <th key={key} className="font-normal break-word px-4 min-w-32 max-w-100 h-10">{ columns[key] }</th>
                )) }
            </tr>
        </thead>
    );
}
