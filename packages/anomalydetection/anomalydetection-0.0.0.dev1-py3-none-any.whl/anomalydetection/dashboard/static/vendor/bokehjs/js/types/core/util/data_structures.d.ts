export declare class MultiDict<T> {
    _dict: {
        [key: string]: T | T[];
    };
    _existing(key: string): T | T[] | null;
    add_value(key: string, value: T): void;
    remove_value(key: string, value: T): void;
    get_one(key: string, duplicate_error: string): T | null;
}
export declare class Set<T> {
    values: T[];
    constructor(obj?: T[] | Set<T>);
    protected _compact(array: T[]): T[];
    push(item: T): void;
    remove(item: T): void;
    length(): number;
    includes(item: T): boolean;
    missing(item: T): boolean;
    slice(from: number, to: number): T[];
    join(str: string): string;
    toString(): string;
    union(set: T[] | Set<T>): Set<T>;
    intersect(set: T[] | Set<T>): Set<T>;
    diff(set: T[] | Set<T>): Set<T>;
}
