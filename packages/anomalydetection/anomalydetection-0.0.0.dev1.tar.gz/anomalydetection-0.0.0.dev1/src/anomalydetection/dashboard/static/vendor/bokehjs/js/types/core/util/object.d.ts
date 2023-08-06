export declare const keys: (o: {}) => string[];
export declare function values<T>(object: {
    [key: string]: T;
}): T[];
export declare function extend<T, T1>(dest: T, src: T1): T & T1;
export declare function extend<T, T1, T2>(dest: T, src1: T1, src2: T2): T & T1 & T2;
export declare function extend<T, T1, T2, T3>(dest: T, src1: T1, src2: T2, src3: T3): T & T1 & T2 & T3;
export declare function clone<T>(obj: T): T;
export declare function merge<T>(obj1: {
    [key: string]: T[];
}, obj2: {
    [key: string]: T[];
}): {
    [key: string]: T[];
};
export declare function size<T>(obj: T): number;
export declare function isEmpty<T>(obj: T): boolean;
