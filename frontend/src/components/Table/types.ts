export type TObj = { [key: string]: any };

export type TCustomRender = { [key: string]: (row: TObj, columnKey: string) => React.ReactNode };

export type TColumns = { [key: string]: string };

export interface ITableProps {
    data: Array<TObj>;
    columns: TColumns;
    customRender?: TCustomRender;
    className?: string;
}