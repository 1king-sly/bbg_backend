/*
  Warnings:

  - Added the required column `password` to the `Organization` table without a default value. This is not possible if the table is not empty.
  - Added the required column `password` to the `Partner` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Organization" ADD COLUMN     "password" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "Partner" ADD COLUMN     "password" TEXT NOT NULL;
