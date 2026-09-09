export type NavigationItem = {
  label: string
  path: string
}

export const navigationItems: NavigationItem[] = [
  {
    label: 'Dashboard',
    path: '/dashboard',
  },
  {
    label: 'Collections',
    path: '/collections',
  },
  {
    label: 'Assets',
    path: '/assets',
  },
  {
    label: 'Processing',
    path: '/processing',
  },
  {
    label: 'Sanitization',
    path: '/sanitization',
  },
  {
    label: 'Disposition',
    path: '/disposition',
  },
  {
    label: 'Reports',
    path: '/reports',
  },
]
