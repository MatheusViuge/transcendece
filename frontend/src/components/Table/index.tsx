import { tv } from "tailwind-variants";
import { Td } from "./Td";
import { THead } from "./THead";
import type { ITableProps } from "./types";

const styles = tv({
    slots: {
        grid: "grid content-start h-fit w-full",
        wrapper: "black-text text-sm text-left leading-5 h-fit w-full border-separate border border-solid border-overlay rounded-[10px] overflow-y-auto",
        table: "w-full border-spacing-0",
    },
});
const { grid, wrapper, table } = styles();

export default function Table({ data, columns, customRender, className="" } : ITableProps) {
    const columnKeys = Object.keys(columns);

    return (
        <div className={grid()}>
            <div className={wrapper({ className })}>
                <table className={table()}>
                    <THead columns={columns} />

                    <tbody>
                        { data.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                { columnKeys.map((columnKey) => (
                                    <Td { ...{
                                        customRender,
                                        row,
                                        columnKey,
                                        key: columnKey
                                    } } />
                                )) }
                            </tr>
                        )) }
                    </tbody>
                </table>
            </div>
        </div>
    );
}


