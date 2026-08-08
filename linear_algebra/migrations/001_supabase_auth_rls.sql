-- ==============================================================================
-- 🔐 SUPABASE POSTGRESQL SCHEMA & ROW LEVEL SECURITY (RLS) MIGRATION
-- Project: Linear Algebra & Field Theory Explorer
-- ==============================================================================

-- 1. Create Public User Profiles Table (Linked to auth.users UUID)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    avatar_url TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS) on Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profiles RLS Policies: Enforce auth.uid() = id
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" 
    ON public.profiles FOR SELECT 
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" 
    ON public.profiles FOR UPDATE 
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile" 
    ON public.profiles FOR INSERT 
    WITH CHECK (auth.uid() = id);


-- 2. Create User Calculation History Table (Linked to auth.users UUID)
CREATE TABLE IF NOT EXISTS public.user_calculation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    module_name TEXT NOT NULL,
    input_data JSONB NOT NULL,
    result_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS) on User Calculation History
ALTER TABLE public.user_calculation_history ENABLE ROW LEVEL SECURITY;

-- User Calculation History RLS Policies: Enforce auth.uid() = user_id
DROP POLICY IF EXISTS "Users can view own calculation history" ON public.user_calculation_history;
CREATE POLICY "Users can view own calculation history" 
    ON public.user_calculation_history FOR SELECT 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own calculation history" ON public.user_calculation_history;
CREATE POLICY "Users can insert own calculation history" 
    ON public.user_calculation_history FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own calculation history" ON public.user_calculation_history;
CREATE POLICY "Users can delete own calculation history" 
    ON public.user_calculation_history FOR DELETE 
    USING (auth.uid() = user_id);


-- 3. Automatic Profile Creation Trigger on New Supabase Auth Signup
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url)
  VALUES (
    NEW.id, 
    COALESCE(NEW.raw_user_meta_data->>'full_name', SPLIT_PART(NEW.email, '@', 1)),
    ''
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger execution on auth.users insert
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
