import type { ReactNode } from "react";

export type TObj = Record<string, ReactNode>;

export type TCustomRender = Record<
    string,
    (row: TObj, columnKey: string) => ReactNode
>;

export type TColumns = Record<string, string>;

export interface ITableProps {
    data: Array<TObj>;
    columns: TColumns;
    customRender?: TCustomRender;
    className?: string;
}
