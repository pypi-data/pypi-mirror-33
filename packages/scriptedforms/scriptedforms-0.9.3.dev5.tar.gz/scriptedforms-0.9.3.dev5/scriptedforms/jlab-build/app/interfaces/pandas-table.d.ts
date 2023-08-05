export interface PandasTable {
    schema: {
        fields: {
            name: string;
            type: string;
        }[];
        primaryKey: string | number;
        pandas_version: string;
    };
    data: {
        [key: string]: string | number;
    }[];
}
