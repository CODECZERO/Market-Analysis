/**
 * Brand CRUD Hooks
 * 
 * Hooks for brand list, detail, create, and delete operations
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getBrands, createBrand, getBrand, deleteBrand } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type {
    BrandDetailResponse,
    BrandListResponse,
    DeleteBrandResponse,
    CreateBrandRequest,
    CreateBrandResponse,
} from "@/types/api";

export function useBrands() {
    return useQuery<BrandListResponse>({
        queryKey: queryKeys.brands(),
        queryFn: getBrands,
    });
}

export function useBrand(brandId: string) {
    return useQuery<BrandDetailResponse>({
        queryKey: queryKeys.brand(brandId),
        queryFn: () => getBrand(brandId),
        enabled: Boolean(brandId),
    });
}

export function useCreateBrand() {
    const queryClient = useQueryClient();
    return useMutation<CreateBrandResponse, Error, CreateBrandRequest>({
        mutationFn: (payload) => createBrand(payload),
        onSuccess: (response) => {
            queryClient.invalidateQueries({ queryKey: queryKeys.brands() });
            if (response?.slug) {
                queryClient.invalidateQueries({ queryKey: queryKeys.brand(response.slug) });
            }
        },
    });
}

export function useDeleteBrand() {
    const queryClient = useQueryClient();
    return useMutation<DeleteBrandResponse, Error, string>({
        mutationFn: (brandId) => deleteBrand(brandId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.brands() });
        },
    });
}
