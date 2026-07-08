import type { TObj, TCustomRender } from "./types";

export function Td ({ customRender, row, columnKey } : { row: TObj, columnKey: string, customRender?: TCustomRender }) {
    const content = customRender && customRender[columnKey]
        ? customRender[columnKey](row, columnKey)
        : row[columnKey];

    return (
        <td
            className="text-ellipsis overflow-hidden whitespace-nowrap py-2 px-4 align-top border-b border-solid border-overlay"
            title={typeof content === 'string' ? content : row[columnKey]?.toString()}
        >
            { content }
        </td>
    );
}