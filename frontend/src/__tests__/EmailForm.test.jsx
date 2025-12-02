import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmailForm from '../components/EmailForm'

describe('EmailForm', () => {
  it('renders email form', () => {
    render(<EmailForm />)
    expect(screen.getByText('받는 사람 이메일 *')).toBeInTheDocument()
    expect(screen.getByText('보내는 사람 이메일 *')).toBeInTheDocument()
    expect(screen.getByText('메일 제목 *')).toBeInTheDocument()
  })
})

